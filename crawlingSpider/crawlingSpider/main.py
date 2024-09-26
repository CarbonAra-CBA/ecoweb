# import networkx as nx
# import matplotlib as plt
import database as db
from search import BFS_Spider
import logging
import json
import os
# json 파일 불러오기 (urls/env_urls.json)
# 반복문으로 json 파일을 순회하면서 상세기관분류를 'name'으로 하고, 사이트링크가 url입니다.

# for:
#     json파일 읽기
#     상세기관분류를 name 변수에 넣기
#     사이트링크를 url 변수에 넣습니다.
'''
eco_url.json 형식
{
  {
    "name": "2050탄소중립 포털",
    "url": "https://www.gihoo.or.kr/"
  },
  {
    "name": "환경부",
    "url": "https://www.me.go.kr/"
  },
  {
...
'''

def main():

    # 크롤링할 사이트 읽기 (절대경로)
    file_path = os.path.join(os.path.dirname(__file__), '../../urls/eco_url.json')
    # eco_url.json 파일 읽기 (eco_url.json : 12개의 가장 탄소중립과 가까운 공공기관 웹사이트, env_urls.json: 환경과 가까운 공공기관 웹사이트 약 200개)
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    # 반복문으로 json 파일을 순회하면서 상세기관분류를 'name'으로 하고, 사이트링크가 url입니다.
    for data in json_data:
        website_name = data['name']
        base_url = data['url']
        print(website_name, base_url)
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)

        logger.info("Starting the application...")

        db.connect_to_database()
        # 사이트명, 사이트 링크를 가져와서 BFS 알고리즘으로 크롤링
        spider = BFS_Spider(base_url, website_name)                  # BFS_Spider 인스턴스 생성
        spider.bfs_search()                                          # BFS 알고리즘으로 크롤링 시작
    
    db.disconnect_from_database()
    # graph = nx.write_gml(spider.graph, "naver_network.gml") # : GML 파일을 읽어 NetworkX 그래프 객체로 변환

    # 그래프 시각화
    # plt.figure(figsize=(12, 12))
    # pos = nx.spring_layout(graph)
    # nx.draw(graph, pos, with_labels=True, node_size=50, font_size=10, font_weight='bold')
    # plt.title("Naver Network Graph")
    # plt.show()

if __name__ == "__main__":
    main()
