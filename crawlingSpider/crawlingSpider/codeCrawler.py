import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,  # 로그의 기본 수준을 설정 (INFO 이상 로그가 기록됨)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 메시지의 포맷을 설정
    handlers=[
        logging.FileHandler("crawler.log", mode='w', encoding='utf-8'),  # 로그를 파일에 저장
        logging.StreamHandler()  # 콘솔에도 동시에 로그를 출력
    ]
)

# codeCrawler.py

class CodeCrawler:
    def __init__(self):
        self.collected_files: List[Dict[str, Any]] = []
        self.session = requests.Session()
        self.visited_files = set()  # 중복 파일 방지용 집합

    def collect_files(self, page_url: str):
        logging.info(f"file collect start: {page_url}")
        response = self.session.get(page_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        content_type = response.headers.get('Content-Type', '')

        # 현재 페이지의 HTML 파일 수집
        if 'html' in content_type:
            self.collected_files.append({
                'filename': 'index.html',
                'code': response.text,
                'type': 'html',
                'url': page_url
            })
            self.visited_files.add(page_url)
        else:
            logging.info(f"Not HTML page: {page_url}")
            return self.collected_files

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for link in soup.find_all(['link', 'script', 'a']):
                file_url = link.get('href') or link.get('src')
                if file_url:
                    full_url = urljoin(page_url, file_url)
                    if self._is_valid_file(full_url) and full_url not in self.visited_files:
                        futures.append(executor.submit(self._fetch_file, full_url))
                        self.visited_files.add(full_url)

            for future in futures:
                file = future.result()
                if file:
                    self.collected_files.append(file)

        logging.info(f"{len(self.collected_files)}file collected")
        return self.collected_files

    def _is_valid_file(self, url: str) -> bool:
        # 유효한 파일인지 확인하는 함수 (특정 패턴 제외)
        excluded_patterns = ['bundle', 'vendor', 'lib', 'cdn', 'jquery', 'bootstrap', 'swiper',
                             'fontawesome', 'react', 'vue', 'angular', 'min.js', 'min.css']
        
        file_name = os.path.basename(urlparse(url).path).lower()  # URL에서 파일 이름 추출
        is_valid_extension = any(file_name.endswith(ext) for ext in ['.html', '.css', '.js'])  # 확장자 확인
        is_not_excluded = not any(pattern in file_name for pattern in excluded_patterns)  # 제외 패턴 확인
        
        return is_valid_extension and is_not_excluded  # 유효성 체크

    def _fetch_file(self, file_url: str) -> Dict[str, Any]:
        # 주어진 URL에서 파일을 가져오는 함수
        try:
            response = self.session.get(file_url)  # 파일 URL 요청
            response.raise_for_status()  # 요청 성공 여부 확인
            file_name = os.path.basename(urlparse(file_url).path)  # URL에서 파일 이름 추출
            return {
                'filename': file_name,
                'code': response.text,  # 파일의 내용
                'type': self._get_file_type(file_name),  # 파일 타입 (html, css, js)
                'url': file_url  # 파일 URL
            }
        except requests.RequestException as e:
            logging.error(f"{file_url} file get error : {e}")
            return None

    def _get_file_type(self, file_name: str) -> str:
        # 파일 타입을 결정하는 함수
        ext = os.path.splitext(file_name)[1].lower()  # 파일 확장자 추출
        if ext == '.html':
            return 'html'
        elif ext == '.css':
            return 'css'
        elif ext == '.js':
            return 'js'
        else:
            return 'unknown'