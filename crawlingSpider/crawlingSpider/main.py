# import networkx as nx
# import matplotlib as plt
import database as db
from search import BFS_Spider
import logging
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# json 파일 불러오기 (urls/env_urls.json)
# 반복문으로 json 파일을 순회하면서 상세기관분류를 'name'으로 하고, 사이트링크가 url입니다.

# for:
#     json파일 읽기
#     상세기관분류를 name 변수에 넣기
#     사이트링크를 url 변수에 넣습니다.
'''
eco_url.json 형식
{`
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

def crawl_website(data):
    # website_name = data['name']
    # base_url = data['url']

    # print(f"Starting crawl for {website_name}: {base_url}")
    website_name = "예비군"
    # spider = BFS_Spider(base_url, website_name)
    spider = BFS_Spider(data, website_name)
    spider.bfs_search()
    
    print(f"Finished crawl for {website_name}: {data}")

def main():

     # 크롤링할 사이트 읽기 (절대경로)
    file_path = os.path.join(os.path.dirname(__file__), '../../urls/eco_url.json')
    # eco_url.json 파일 읽기 (eco_url.json : 12개의 가장 탄소중립과 가까운 공공기관 웹사이트, env_urls.json: 환경과 가까운 공공기관 웹사이트 약 200개)
    
    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = json.load(file)


    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting the application...")
    crawl_website("https://www.yebigun1.mil.kr/dmobis/index_main.do")
    # db.connect_to_database()
    # 멀티쓰레딩 쓰레드 12개로 크롤링
    # with ThreadPoolExecutor(max_workers=12) as executor:
    #     future_to_site = {executor.submit(crawl_website, data): data for data in json_data} # submit: 작업을 쓰레드에 제출, future 객체 반환

    #     # 완료된 작업 처리
    #     for future in as_completed(future_to_site): # as_completed: 완료된 작업을 순서대로 반환 
    #         data = future_to_site[future]
    #         try:
    #             future.result() # result: 작업의 결과를 반환
    #         except Exception as exc:
    #             print(f"{data['name']} generated an exception: {exc}")
    
    # db.disconnect_from_database()


if __name__ == "__main__":
    main()
