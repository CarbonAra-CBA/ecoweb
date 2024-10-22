import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from driver import init_driver
from items import codeItem
logging.basicConfig(
    level=logging.INFO,  # 로그의 기본 수준을 설정 (INFO 이상 로그가 기록됨)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 메시지의 포맷을 설정
    handlers=[
        logging.FileHandler("crawlerSecond.log", mode='w', encoding='utf-8'),  # 로그를 파일에 저장
        logging.StreamHandler()  # 콘솔에도 동시에 로그를 출력
    ]
)

class CodeCrawler:
    
    def __init__(self):
        self.collected_files: List[codeItem] = []
        self.session = requests.Session()
        self.visited_files = set()

    def collect_files(self, page_url: str):
        try:
            driver = init_driver()
            driver.get(page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            logging.info(f"file collect start: {page_url}")

            # HTML 수집
            html = driver.page_source
            html_code_item = codeItem(
                url=page_url,
                file_name='index.html',
                type='html',
                code=html
            )
            self.collected_files.append(html_code_item)

            # JS와 CSS 리소스 수집
            js_resources = self._get_js_resources(driver)
            css_resources = self._get_css_resources(driver)

            # ThreadPoolExecutor를 사용하여 JS와 CSS 파일 병렬 처리
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {
                    executor.submit(self._fetch_file, url): url 
                    for url in js_resources + css_resources
                    if self._is_valid_file(url) and url not in self.visited_files
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        file = future.result()
                        if file:
                            self.collected_files.append(file)
                            self.visited_files.add(url)
                    except Exception as exc:
                        logging.error(f'{url} generated an exception: {exc}')

            logging.info(f"{len(self.collected_files)} files collected")
            
            return self.collected_files
        except Exception as e:
            logging.error(f"Error collecting files from {page_url}: {str(e)}")
            return []
        finally:
            driver.quit()

    def _is_valid_file(self, url: str) -> bool:
        # 유효한 파일인지 확인하는 함수 (특정 패턴 제외)
        excluded_patterns = ['bundle', 'vendor','lib', 'cdn', 'jquery', 'bootstrap', 'swiper',
                             'fontawesome', 'react', 'vue', 'angular', 'min.js', 'min.css','cdnjs', 'jsdelivr', 'googleapis', 'bootstrapcdn']
        
        file_name = os.path.basename(urlparse(url).path).lower()  # URL에서 파일 이름 추출
        is_valid_extension = any(file_name.endswith(ext) for ext in ['.html', '.css', '.js'])  # 확장자 확인
        is_not_excluded = not any(pattern in file_name for pattern in excluded_patterns)  # 제외 패턴 확인
        
        return is_valid_extension and is_not_excluded  # 유효성 체크

    def _fetch_file(self, file_url: str) -> codeItem:
        try:
            response = self.session.get(file_url)
            response.raise_for_status()
            content = response.text
            file_name = os.path.basename(urlparse(file_url).path)
            file_type = self._get_file_type(file_name)
            return codeItem(
                url=file_url,
                file_name=file_name,
                type=file_type,
                code=content
            )
        except Exception as e:
            logging.error(f"Error fetching file {file_url}: {e}")
            return None

    def _get_file_type(self, file_name: str) -> str:
        ext = os.path.splitext(file_name)[1].lower()
        if ext == '.html':
            return 'html'
        elif ext == '.css':
            return 'css'
        elif ext == '.js':
            return 'js'
        else:
            return 'unknown'

    def _get_js_resources(self, driver):
        return driver.execute_script("""
            var js_resources = [];
            var scripts = document.getElementsByTagName('script');
            for(var i = 0; i < scripts.length; i++) {
                if(scripts[i].src) js_resources.push(scripts[i].src);
            }
            return js_resources;
        """)

    def _get_css_resources(self, driver):
        return driver.execute_script("""
            var css_resources = [];
            var links = document.getElementsByTagName('link');
            for(var i = 0; i < links.length; i++) {
                if(links[i].rel === 'stylesheet') css_resources.push(links[i].href);
            }
            return css_resources;
        """)
