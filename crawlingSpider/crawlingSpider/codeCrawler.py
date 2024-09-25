import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CodeCrawler:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.collected_files: List[Dict[str, Any]] = []

    def _is_valid_file(self, url: str) -> bool:
        excluded_patterns = ['bundle', 'vendor', 'lib', 'cdn', 'jquery', 'bootstrap', 'min.js']
        return not any(pattern in url.lower() for pattern in excluded_patterns)

    def _fetch_file(self, url: str) -> Dict[str, Any] | None:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type', '')
            
            if 'html' in content_type:
                file_type = 'html'
            elif 'javascript' in content_type:
                file_type = 'js'
            else:
                return None

            return {
                'url': url,
                'content': response.text,
                'type': file_type
            }
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def collect_files(self):
        logging.info(f"Collecting files from: {self.base_url}")
        response = self.session.get(self.base_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        urls_to_fetch = [self.base_url]  # Include the base URL to fetch HTML
        for script in soup.find_all('script', src=True):
            urls_to_fetch.append(urljoin(self.base_url, script['src']))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._fetch_file, url) for url in urls_to_fetch if self._is_valid_file(url)]
            for future in futures:
                result = future.result()
                if result:
                    self.collected_files.append(result)

        logging.info(f"Collected {len(self.collected_files)} files")

def main():
    base_url = "https://www.gov.kr/portal/main/nologin"
    crawler = CodeCrawler(base_url)
    crawler.collect_files()

    for file in crawler.collected_files:
        print(f"URL: {file['url']}")
        print(f"Type: {file['type']}")
        print(f"Content (first 100 chars): {file['content'][:100]}...")
        print("---")

if __name__ == "__main__":
    main()