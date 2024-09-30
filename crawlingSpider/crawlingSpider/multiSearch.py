from collections import deque
import sys
import os
# 현재 파일의 상위 디렉토리 경로를 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from urllib.parse import urlparse, urljoin
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from traffic import trafficSpider
from driver import Driver
from database import save_to_database # 데이터베이스 저장 함수
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import networkx as nx
from codeCrawler import CodeCrawler 
'''
고병수] 크롤링을 위한 BFS 알고리즘 구현
- 큐로 구현한 BFS 입니다.
- 깊이는 최대 3으로 하겠음 (논문에 근거하였음))
- 크롤링할 URL 배열 필요 (= crawling_URLS)

고병수] 08/29
depth 구현하기 위해서 dict 로 depth와 함께 queue에 저장하겠음. (그럼 set으로 중복
'''


class BFS_Spider:
    def __init__(self, base_url, website_name):

        parsed_base_url = urlparse(base_url)    # base_url에서 도메인 부분만 추출
        self.base_url = parsed_base_url.netloc  # naver.com
        self.visited = {}
        self.queue = deque([(base_url,0)])      # 튜플로 URL과 깊이를 저장
        self.link_extractor = LinkExtractor()
        self.spider = trafficSpider()           # trafficSpider 인스턴스 생성
        self.code_crawler = CodeCrawler(base_url)
        self.website_name = website_name        # 사이트명
        # self.graph = nx.DiGraph()             # 그래프 생성 (유향 그래프)
        self.driver = Driver().init_driver()    # 드라이버를 초기화하고 유지

    def bfs_search(self):
        try:
            while self.queue:                                                                  # 큐가 전부 빈 상태가 될 때까지 진행합니다.
                current_url, current_depth = self.queue.popleft()
                if current_depth >= 4:                                                         # 깊이 3까지 진행
                    break
                if current_url in self.visited:                                                # 방문한 url이라면, 큐에 추가하지 않음
                    continue
                self.visited[current_url] = current_depth                                      # 현재 깊이 저장
                try:
                    traffic_data = self.spider.crawling_items(current_url, self.driver)
                    traffic_data['depth'] = current_depth
                    print(current_url + "'s traffic_data:", traffic_data,"depth:",current_depth)
                    code_data = self.code_crawler.collect_files()                              # 코드 데이터 (html,js)
                    # 트래픽 데이터와 코드 데이터를 합쳐서 하나의 데이터로 저장
                    save_to_database(self.website_name,current_url,traffic_data,code_data) ,
                                                               
                    # self.graph.add_node(current_url) # 현재 URL을 노드로 추가 (일단 네트워크 노드는 보류)

                    # 현재 링크의 내부에서 subdomain, subpath를 조사합니다.
                    links = self.extract_links(current_url)                                     # 현재 URL에서 링크 추출
                    
                    for link in links:
                        if link not in self.visited:
                            self.queue.append((link, current_depth + 1))                        # 다음 깊이로 큐에 추가
                        # 링크를 엣지로 추가(보류)
                        # self.graph.add_edge(current_url, link) 
                except WebDriverException as e:                                                 # 위험한 방법이지만, 오류의 원인을 찾지 못 했음으로 크게 예외처리하겠음. Todo: 예외처리 세분화
                    print(f"Error while processing {current_url}: {e}")
                    continue
        finally:
            self.driver.quit()                                                                  # 크롤링이 끝난 후 드라이버를 종료합니다.

    def extract_links(self, url):
        response = self.fetch_response(url, self.driver)                                        # page_source를 가져옵니다.
        links = self.link_extractor.extract_links(response)                                     # (a tags)링크를 추출합니다.
        return [urljoin(url, link.url) for link in links if self.is_valid_link(link.url)]

    def fetch_response(self, url, driver):
        try:
            driver.get(url)
            html = driver.page_source
        except TimeoutException:
            print(f"Timeout while loading {url}")
            html = ''
        finally:
            time.sleep(2)  # 세션 종료 후 대기 시간 추가
        # HtmlResponse 객체 생성
        response = HtmlResponse(url=url, body=html, encoding='utf-8')
        return response

    def is_valid_link(self, link):
        parsed_link = urlparse(link)
        return parsed_link.netloc.endswith(self.base_url)

