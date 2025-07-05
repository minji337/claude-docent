from typing import Tuple
from collections import defaultdict
from typing import DefaultDict

search_result_1 = [
    "서울에서 루프탑 바 야경 좋은 곳 추천해줘" ,
    "서울에서 루프top bar 밤 풍경 소개 부탁!",
    "추천 서울 탑 루프 바",
    "서울에 있는 루프가 있는 바 추천해줘",
    "서울 지붕 옥탑 바 야경"
]

search_result_2 = [
    "서울에서 루프탑 바 야경 좋은 곳 추천해줘" ,
    "서울에 있는 루프가 있는 바 추천해줘",
    "서울에서 루프top bar 밤 풍경 소개 부탁!",
    "추천 서울 탑 루프 바",
    "서울 지붕 옥탑 바 야경"
]

def get_rrf(
    ranked_lists: list[list[str]],
    k: int = 60,
    weights: list[float] | None = None,
) -> list[Tuple[str, float]]:
    weights = weights or [1 / len(ranked_lists)] * len(ranked_lists)
    scores: DefaultDict[str, float] = defaultdict(float)
    for weight, ranked_list in zip(weights, ranked_lists):
        for rank, element in enumerate(ranked_list, start=1): 
            score = weight / (k + rank)
            scores[element] += score

    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

results = get_rrf(ranked_lists=[search_result_1, search_result_2], weights=[0.5, 0.5])
print(results)
