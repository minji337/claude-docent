from pathlib import Path


class Relics:

    def __init__(self):
        self.database, self.ids = self._load_database()
        self.index = -1
        self.presented: set[str] = set()

    def _load_database(self):
        database = {
            "1": {
                "header": "2점 중 1번째 이미지",
                "img_path": "data/relic1.png",
                "title": "1번 전시물",
                "is_presented": False,
            },
            "2": {
                "header": "2점 중 2번째 이미지",
                "img_path": "data/relic2.png",
                "title": "2번 전시물 ",
                "is_presented": False,
            },
        }
        ids = list(database.keys())
        return database, ids

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
    def header(self):
        return f"{len(self.database)}점 중 {self.index + 1}번째 전시물입니다."

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
