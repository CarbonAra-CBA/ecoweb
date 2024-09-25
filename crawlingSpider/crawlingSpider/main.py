import networkx as nx
import matplotlib as plt

from search import BFS_Spider

# json 파일 불러오기 (urls/env_urls.json)
# 반복문으로 json 파일을 순회하면서 상세기관분류를 'name'으로 하고, 사이트링크가 url입니다.
for:
    json파일 읽기
    상세기관분류를 name 변수에 넣기
    사이트링크를 url 변수에 넣습니다.
'''
{
        "기관유형": "중앙행정기관",
        "기관분류": "환경부",
        "상세기관분류": "환경부",
        "사이트명": "생활환경안전정보포털",
        "사이트 구분": "웹",
        "사이트링크": "http://ecolife.me.go.kr"
    }
'''

# 사이트명, 사이트 링크를 가져와서 BFS 알고리즘으로 크롤링
# 크롤링 결과를 aws rds에 저장

base_url = "https://naver.com"     # "naver.com"
spider = BFS_Spider(base_url)                                # BFS_Spider 인스턴스 생성
spider.bfs_search()                                          # BFS 알고리즘으로 크롤링 시작
# graph = nx.write_gml(spider.graph, "naver_network.gml") # : GML 파일을 읽어 NetworkX 그래프 객체로 변환

# 그래프 시각화
# plt.figure(figsize=(12, 12))
# pos = nx.spring_layout(graph)
# nx.draw(graph, pos, with_labels=True, node_size=50, font_size=10, font_weight='bold')
# plt.title("Naver Network Graph")
# plt.show()
