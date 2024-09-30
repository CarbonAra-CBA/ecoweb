from collections import deque
import sys
import os
import logging
from urllib.parse import urlparse, urljoin
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from traffic import trafficSpider
from driver import Driver
from database import save_to_database_website, save_to_database_traffic  # 데이터베이스 저장 함수
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
from codeCrawler import CodeCrawler

logging.basicConfig(
    level=logging.INFO,  # 로그의 기본 수준을 설정 (INFO 이상 로그가 기록됨)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 메시지의 포맷을 설정
    handlers=[
        logging.FileHandler("search.log", mode='w', encoding='utf-8'),  # 로그를 파일에 저장
        logging.StreamHandler()  # 콘솔에도 동시에 로그를 출력
    ]
)


class BFS_Spider:
    def __init__(self, base_url, website_name):
        parsed_base_url = urlparse(base_url)    # base_url에서 도메인 부분만 추출
        self.base_url = parsed_base_url.netloc  # naver.com
        self.visited = {}
        self.queue = deque([(base_url, 0)])     # 튜플로 URL과 깊이를 저장
        self.link_extractor = LinkExtractor()
        self.spider = trafficSpider()           # trafficSpider 인스턴스 생성
        self.code_crawler = CodeCrawler()
        self.website_name = website_name        # 사이트명
        self.driver = Driver().init_driver()    # 드라이버를 초기화하고 유지
        self.retries = 3  # 재시도 횟수
        self.delay = 5    # 재시도 대기 시간 (초)

    def bfs_search(self):
        try:
            all_links = set()
            while self.queue:  # 큐가 전부 빈 상태가 될 때까지 진행합니다.
                current_url, current_depth = self.queue.popleft()
                if current_depth >= 4:  # 깊이 3까지 진행
                    break
                if current_url in self.visited:
                    continue
                self.visited[current_url] = current_depth  # 현재 깊이 저장
                try:
                    links = self.extract_links(current_url)  # 현재 URL에서 링크 추출
                    logging.info(f"Collected {len(links)} links from {current_url}")
                    for link in links:
                        if link not in self.visited:
                            all_links.add(link)
                            self.queue.append((link, current_depth + 1))  # 다음 깊이로 큐에 추가
                except WebDriverException as e:
                    logging.error(f"Error while processing {current_url}: {e}")
                    continue
            logging.info(f"All links collected: {len(all_links)}")  # 총 수집된 링크 수 출력
            self.driver.quit() 

            self.driver = Driver().init_driver()
            # 링크를 순차적으로 처리
            total_links = len(all_links)
            completed_links = 0
            for link in all_links:
                try:
                    self.process_link(link)
                    completed_links += 1
                    logging.info(f"Progress: {completed_links}/{total_links} ...")  # 진행 상황 출력
                except Exception as e:
                    logging.error(f"Error processing {link}: {e}")
        finally:
            self.driver.quit()  # 크롤링이 끝난 후 드라이버를 종료합니다.

    def process_link(self, link):
        traffic_data = self.spider.crawling_items(link,self.driver)
        code_data = self.code_crawler.collect_files(link)
        for d in code_data:
            website_data = {
                'website_name': self.website_name,
                'url': d['url'],
                'current_url': link,
                'file_name': d['filename'],
                'type': d['type'],
                'code': d['code'],
            }
            
            save_to_database_website(website_data)
        logging.info(f"Saving traffic data to database: {traffic_data['url']}")
        save_to_database_traffic(traffic_data)

    def fetch_response(self, url, driver):
        for attempt in range(self.retries):
            try:
                driver.get(url)
                html = driver.page_source
                response = HtmlResponse(url=url, body=html, encoding='utf-8')
                return response
            except TimeoutException:
                logging.error(f"Error connection : {url}")
                logging.info(f"Timeout while loading : {url}, retrying ({attempt + 1}/{self.retries})...")
                time.sleep(self.delay)
            except WebDriverException as e:
                logging.error(f"Error while loading : {url} : {e}")
                break
        return HtmlResponse(url=url, body='', encoding='utf-8')

    def extract_links(self, url):
        response = self.fetch_response(url, self.driver)  # page_source를 가져옵니다.
        links = self.link_extractor.extract_links(response)  # (a tags)링크를 추출합니다.
        return [urljoin(url, link.url) for link in links if self.is_valid_link(link.url)]

    def is_valid_link(self, link):
        parsed_link = urlparse(link)
        return parsed_link.netloc.endswith(self.base_url)
