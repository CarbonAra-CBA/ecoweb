from collections import deque
from urllib.parse import urlparse, urljoin
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from traffic import trafficSpider
from driver import Driver
from database import save_to_database  # 데이터베이스 저장 함수
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import networkx as nx
'''
고병수] 크롤링을 위한 BFS 알고리즘 구현
- 큐로 구현한 BFS 입니다.
- 현재 naver.com 으로 하드코딩되어있습니다. (TODO: 사용자가 입력한 URL로 변경)
'''
class BFS_Spider:
    def __init__(self, base_url):
        self.base_url = base_url
        self.visited = set()
        self.queue = deque([base_url])          # 일단 큐에 base_url을 넣어둡니다.
        self.link_extractor = LinkExtractor()
        self.spider = trafficSpider()           # trafficSpider 인스턴스 생성
        self.graph = nx.DiGraph()               # 그래프 생성 (유향 그래프)
        self.driver = Driver().init_driver()    # 드라이버를 초기화하고 유지

    def bfs_search(self):
        try:
            while self.queue:  # 큐가 전부 빈 상태가 될 때까지 진행합니다.
                current_url = self.queue.popleft()
                if current_url in self.visited:
                    continue

                self.visited.add(current_url)
                try:
                    traffic_data = self.spider.crawling_items(current_url, self.driver)
                    print(current_url + "'s traffic_data:", traffic_data)
                    # save_to_database(traffic_data)                                            # 트래픽 데이터를 데이터베이스에 저장 (일단 DB는 메서드가 모두 오류없이 작동할때 확인하겠음)

                    # 현재 URL을 노드로 추가
                    self.graph.add_node(current_url)

                    # 현재 링크의 내부에서 subdomain, subpath를 조사합니다.
                    links = self.extract_links(current_url)  # 현재 URL에서 링크 추출
                    for link in links:
                        if link not in self.visited:
                            self.queue.append(link)
                        # 링크를 엣지로 추가
                        self.graph.add_edge(current_url, link)
                except WebDriverException as e:                                                 # 위험한 방법이지만, 오류의 원인을 찾지 못 했음으로 크게 예외처리하겠음. Todo: 예외처리 세분화
                    print(f"Error while processing {current_url}: {e}")
                    continue
        finally:
            self.driver.quit()                                                                  # 크롤링이 끝난 후 드라이버를 종료합니다.

    def extract_links(self, url):
        response = self.fetch_response(url, self.driver)
        links = self.link_extractor.extract_links(response)
        return [urljoin(url, link.url) for link in links if self.is_valid_link(link.url)]

    def fetch_response(self,url, driver):
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
        return parsed_link.netloc.endswith("naver.com")

