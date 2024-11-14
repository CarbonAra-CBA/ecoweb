'''
bfs 없이 루트만 크롤링하는 코드

루트의 네트워크 트래픽만 크롤링해서 데이터베이스에 저장한다.
크드와 네트워크 트래픽 크롤링 코드는 따로 작성한다.
1) 네트워크 트래픽만 크롤링
2) 데이터베이스에 저장

3) 코드 크롤링 코드 
4) 데이터베이스에 저장

5) webpage에서 url 입력시 Db에서 해당 url 찾는다. 
if 만약 있으면 
    DB에서 조회해서 Webpage에 전달
    
else 만약 DB에 없으면
    크롤링 후 DB에 저장
    DB에서 호출 


'''
import csv
import json
from traffic import trafficSpider
from codeCrawler import CodeCrawler
from search import BFS_Spider

def main():
    # json 파일 읽기
    
    with open('../../urls/env_urls.json', 'r', encoding='utf-8') as file:
        env_urls = json.load(file)
    
    # 루트의 네트워크 트래픽과 코드 크롤링
    for url in env_urls:
        bfs_spider = BFS_Spider(url['사이트링크'],url['사이트명'])
        bfs_spider.process_link(url['사이트링크']) # bfs 없이 link만 크롤링합니다.
    pass

if __name__ == "__main__":
    main()