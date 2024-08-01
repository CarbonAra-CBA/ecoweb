# import networkx as nx
from collections import deque
from urllib.parse import urlparse, urljoin
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from traffic import trafficSpider
from driver import Driver
from database import save_to_database  # 데이터베이스 저장 함수
from driver import Driver

'''
고병수] 크롤링을 위한 BFS 알고리즘 구현
- 큐로 구현한 BFS 입니다.
- 현재 naver.com 으로 하드코딩되어있습니다. (TODO: 사용자가 입력한 URL로 변경)

'''
class BFS_Spider:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.queue = deque([base_url])
        self.link_extractor = LinkExtractor()
        self.spider = trafficSpider()  # trafficSpider 인스턴스 생성

    def bfs_search(self):
        while self.queue:
            current_url = self.queue.popleft()
            if current_url in self.visited:                         # 음.. 이거 필요한가??
                continue

            self.visited.add(current_url)                           # 방문 처리하기
            traffic_data = self.spider.crawling_items(current_url)  # 트래픽 측정을 위한 크롤링
            print(current_url + "'s traffic_data:", traffic_data)
            # save_to_database(traffic_data)                        # 트래픽 데이터를 데이터베이스에 저장 (일단 DB는 메서드가 모두 오류없이 작동할때 확인하겠음)




            # 연결 관계를 형성하여 queue에 추가                         # 이상함.
            links = self.extract_links(current_url)
            for link in links:
                if link not in self.visited:
                    self.queue.append(link)

    def process_url(self, url):
        spider = trafficSpider()
        return spider.crawling_items(url)

    def extract_links(self, url):
        response = self.fetch_response(url)
        links = self.link_extractor.extract_links(response)
        return [urljoin(url, link.url) for link in links if self.is_valid_link(link.url)]

    def fetch_response(self, url):
        driver = Driver().init_driver()
        driver.get(url)
        html = driver.page_source
        driver.quit()
        # HtmlResponse 객체 생성
        response = HtmlResponse(url=url, body=html, encoding='utf-8')
        return response

    def is_valid_link(self, link):
        parsed_link = urlparse(link)
        return parsed_link.netloc.endswith("naver.com")


