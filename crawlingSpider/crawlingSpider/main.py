from search import BFS_Spider
import networkx as nx
import matplotlib as plt

base_url = "https://www.naver.com"
spider = BFS_Spider(base_url)                                # BFS_Spider 인스턴스 생성
spider.bfs_search()                                          # BFS 알고리즘으로 크롤링 시작
graph = nx.write_gml(spider.graph, "naver_network.gml") # : GML 파일을 읽어 NetworkX 그래프 객체로 변환

# 그래프 시각화
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(graph)
nx.draw(graph, pos, with_labels=True, node_size=50, font_size=10, font_weight='bold')
plt.title("Naver Network Graph")
plt.show()
