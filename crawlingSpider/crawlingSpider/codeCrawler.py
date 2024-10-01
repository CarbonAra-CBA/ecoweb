import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from driver import init_driver

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
        self.collected_files: List[Dict[str, Any]] = []
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
            self.collected_files.append({
                'filename': 'index.html',
                'code': html,
                'type': 'html',
                'url': page_url
            })
            self.visited_files.add(page_url)

            # CSS와 JS 파일 수집
            resources = driver.execute_script("""
                var resources = [];
                var scripts = document.getElementsByTagName('script');
                var links = document.getElementsByTagName('link');
                
                for(var i = 0; i < scripts.length; i++) {
                    if(scripts[i].src) resources.push(scripts[i].src);
                }
                
                for(var i = 0; i < links.length; i++) {
                    if(links[i].rel === 'stylesheet') resources.push(links[i].href);
                }
                
                return resources;
            """)

            with ThreadPoolExecutor(max_workers=5) as executor:
                files = []
                for resource in resources:
                    full_url = urljoin(page_url, resource)
                    if self._is_valid_file(full_url) and full_url not in self.visited_files:
                        files.append(executor.submit(self._fetch_file, full_url))
                        self.visited_files.add(full_url)

                for future in files:
                    file = future.result()
                    if file:
                        self.collected_files.append(file)

            logging.info(f"{len(self.collected_files)} files collected")
            
            return self.collected_files
        except Exception as e:
            logging.error(f"Error collecting files from {page_url}: {str(e)}")
            return []
        finally:
            driver.quit()

    def _is_valid_file(self, url: str) -> bool:
        # 유효한 파일인지 확인하는 함수 (특정 패턴 제외)
        excluded_patterns = ['bundle', 'vendor', 'lib', 'cdn', 'jquery', 'bootstrap', 'swiper',
                             'fontawesome', 'react', 'vue', 'angular', 'min.js', 'min.css']
        
        file_name = os.path.basename(urlparse(url).path).lower()  # URL에서 파일 이름 추출
        is_valid_extension = any(file_name.endswith(ext) for ext in ['.html', '.css', '.js'])  # 확장자 확인
        is_not_excluded = not any(pattern in file_name for pattern in excluded_patterns)  # 제외 패턴 확인
        
        return is_valid_extension and is_not_excluded  # 유효성 체크

    def _fetch_file(self, file_url: str) -> Dict[str, Any]:
        try:
            response = self.session.get(file_url)
            response.raise_for_status()
            content = response.text
            file_name = os.path.basename(urlparse(file_url).path)
            return {
                'filename': file_name,
                'code': content,
                'type': self._get_file_type(file_name),
                'url': file_url
            }
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

