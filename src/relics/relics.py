from pathlib import Path
import json

class RelicsLoader:

    def __init__(self):        
        self.database = self.load_database()        

    def load_database(self):
        file_path = Path("data") / "database" / "relic_index.json"
        with open(file_path, encoding="utf-8") as f:
            database = json.load(f)
        for key, value in database.items():
            value["img_path"] = str(
                Path("data", "database", key, Path(value["img"]).name)
            )
            value["title"] = f"{value['label']['명칭']} ({key})"
        self.ids = list(database.keys())
        return database

    def get_database(self):
        return self.database.copy(), self.ids


relics_loader = RelicsLoader()


class Relics:

    def __init__(self, database: dict | None = None):
        if database is None:
            self.database, self.ids = relics_loader.get_database()
            self.original = self
            self.presented: set[str] = set()
        else:
            self.database = database
            self.original = None
            self.presented: set[str] = set()
        self.index = -1

    @property
    def current_id(self):
        return self.ids[self.index]

    @property
    def current(self):
        current_relic = self.database[self.current_id]
        return current_relic

    def next(self):
        self.index += 1
        return self.current

    def previous(self):
        if self.index == 0:
            raise ValueError("현재 첫 번째 작품을 보고 있습니다.")
        else:
            self.index -= 1
        return self.current

    @property
    def original_database(self):
        return self.database

    @property
    def header(self):
        prefix = "검색된 작품" if isinstance(self, SearchedRelics) else ""
        return f"{prefix} {len(self.database)}점 중 {self.index + 1}번째 전시물입니다."

    def set_presented(self, value: bool = True):
        if value:
            self.presented.add(self.current_id)
        else:
            self.presented.discard(self.current_id)

    def is_presented(self, id: str | None = None) -> bool:
        return (id or self.current_id) in self.presented

    def current_to_card(self):
        return {
            "header": self.header,
            "img_path": self.current["img_path"],
            "title": self.current["title"],
        }


class SearchedRelics(Relics):

    def __init__(self, searched_database: dict, original: Relics):
        super().__init__(searched_database)
        self.original = original
        self.ids = list(self.database.keys())

    @property
    def original_database(self):
        return self.original.database
