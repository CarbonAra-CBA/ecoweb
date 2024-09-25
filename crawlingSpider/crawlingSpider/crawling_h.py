import os
import requests
import pandas as pd
import networkx as nx
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModel
import torch
import json
import re

# 로깅 설정: 프로그램 실행 중 발생하는 정보를 기록합니다.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CodeCrawler:
    def __init__(self, base_url: str):
        # 클래스 초기화: 웹사이트의 기본 URL을 설정하고 필요한 변수들을 초기화합니다.
        self.base_url = base_url
        self.collected_files: List[Dict[str, Any]] = []  # 수집된 파일들을 저장할 리스트
        self.link_index = nx.DiGraph()  # 파일 간의 링크를 저장할 그래프
        self.session = requests.Session()  # HTTP 요청을 보낼 세션
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/graphcodebert-base")  # 코드 분석을 위한 토크나이저
        self.model = AutoModel.from_pretrained("microsoft/graphcodebert-base")  # 코드 분석을 위한 모델

    def collect_files(self):
        # 웹사이트에서 파일을 수집하는 함수
        logging.info(f"파일 수집 중: {self.base_url}")
        response = self.session.get(self.base_url)  # 기본 URL에서 HTML 페이지를 가져옵니다.
        soup = BeautifulSoup(response.text, 'html.parser')  # HTML을 파싱합니다.
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for link in soup.find_all(['link', 'script']):  # HTML에서 모든 링크와 스크립트 태그를 찾습니다.
                file_url = link.get('href') or link.get('src')  # 링크나 스크립트의 URL을 가져옵니다.
                if file_url:
                    full_url = urljoin(self.base_url, file_url)  # 상대 URL을 절대 URL로 변환합니다.
                    if self._is_valid_file(full_url):  # 유효한 파일인지 확인합니다.
                        futures.append(executor.submit(self._fetch_file, full_url))  # 파일을 가져오는 작업을 비동기로 실행합니다.
            
            for future in futures:
                file = future.result()  # 비동기 작업의 결과를 가져옵니다.
                if file:
                    self.collected_files.append(file)  # 수집된 파일을 리스트에 추가합니다.
        
        logging.info(f"{len(self.collected_files)}개의 파일을 수집했습니다")

    def _is_valid_file(self, url: str) -> bool:
        # 파일이 유효한지 확인하는 함수
        excluded_patterns = [
            'bundle', 'vendor', 'lib', 'cdn',
            'jquery', 'bootstrap', 'swiper',
            'fontawesome', 'react', 'vue', 'angular',
            'min.js', 'min.css'
        ]
        
        file_name = os.path.basename(urlparse(url).path).lower()  # URL에서 파일 이름을 추출합니다.
        is_valid_extension = any(file_name.endswith(ext) for ext in ['.html', '.css', '.js'])  # 유효한 확장자인지 확인합니다.
        is_not_excluded = not any(pattern in file_name for pattern in excluded_patterns)  # 제외된 패턴이 포함되지 않았는지 확인합니다.
        
        return is_valid_extension and is_not_excluded  # 유효한 파일인지 여부를 반환합니다.

    def _fetch_file(self, file_url: str) -> Dict[str, Any]:
        # 파일을 가져오는 함수
        try:
            response = self.session.get(file_url)  # 파일 URL에서 내용을 가져옵니다.
            response.raise_for_status()  # 요청이 성공했는지 확인합니다.
            file_name = os.path.basename(urlparse(file_url).path)  # URL에서 파일 이름을 추출합니다.
            return {
                'name': file_name,
                'content': response.text,
                'type': self._get_file_type(file_name),
                'url': file_url
            }
        except requests.RequestException as e:
            logging.error(f"{file_url} 파일을 가져오는 중 오류 발생: {e}")
            return None

    def _get_file_type(self, file_name: str) -> str:
        # 파일 타입을 확인하는 함수
        ext = os.path.splitext(file_name)[1].lower()  # 파일 확장자를 추출합니다.
        if ext == '.html':
            return 'html'
        elif ext == '.css':
            return 'css'
        elif ext == '.js':
            return 'js'
        else:
            return 'unknown'

    def _remove_comments(self, content: str, file_type: str) -> str:
        # 파일에서 주석을 제거하는 함수
        if file_type == 'html':
            return re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)  # HTML 주석 제거
        elif file_type == 'css':
            return re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)  # CSS 주석 제거
        elif file_type == 'js':
            return re.sub(r'//.*?$|/\*.*?\*/', '', content, flags=re.MULTILINE|re.DOTALL)  # JS 주석 제거
        return content

    def _remove_whitespace(self, content: str) -> str:
        # 파일에서 불필요한 공백을 제거하는 함수
        return re.sub(r'\s+', ' ', content).strip()

    def create_link_index(self):
        # 파일 간의 링크 인덱스를 생성하는 함수
        logging.info("링크 인덱스 생성 중")
        for file in self.collected_files:
            self.link_index.add_node(file['name'])  # 파일을 그래프의 노드로 추가합니다.
            if file['type'] == 'html':
                self._extract_links_from_html(file)  # HTML 파일에서 링크를 추출합니다.
            elif file['type'] == 'js':
                self._extract_links_from_js(file)  # JS 파일에서 링크를 추출합니다.

    def _extract_links_from_html(self, file: Dict[str, Any]):
        # HTML 파일에서 링크를 추출하는 함수
        soup = BeautifulSoup(file['content'], 'html.parser')
        for link in soup.find_all(['link', 'script']):
            href = link.get('href') or link.get('src')
            if href:
                linked_file = os.path.basename(urlparse(href).path)
                self.link_index.add_edge(file['name'], linked_file)  # 링크된 파일을 그래프의 엣지로 추가합니다.

    def _extract_links_from_js(self, file: Dict[str, Any]):
        # JS 파일에서 링크를 추출하는 함수
        imports = re.findall(r'import.*?[\'"](.+?)[\'"]', file['content'])
        for imp in imports:
            linked_file = os.path.basename(imp)
            self.link_index.add_edge(file['name'], linked_file)  # 링크된 파일을 그래프의 엣지로 추가합니다.

    def analyze_file(self, file: Dict[str, Any]) -> Dict[str, Any]:
        # 파일을 분석하는 함수
        logging.info(f"파일 분석 중: {file['name']}")
        file_type = file['type']
        content = file['content']

        tokenized_content = self.tokenizer.tokenize(content)  # 파일 내용을 토큰화합니다.
        if len(tokenized_content) > 512:
            logging.info(f"코드가 너무 길어 512 토큰으로 잘라서 분석합니다.")
            content_chunks = [tokenized_content[i:i + 512] for i in range(0, len(tokenized_content), 512)]
            results = []
            for chunk in content_chunks:
                prompt = f"""
                You are analyzing a {file_type.upper()} file for potential issues.
                Please list the issues found in the following code related to the following categories:
                1. Redundant Code: Any unnecessary or duplicate code.
                2. Security Vulnerabilities: Any potential exposure of sensitive information or security risks.
                3. High Complexity: Any complex or unoptimized code.
                4. Performance Issues: Any code that may lead to slow performance or inefficiency.
                5. Accessibility Issues: Any issues that could hinder accessibility (for HTML files).
                6. Interactivity Issues: Problems with user interaction or dynamic behavior (for JS files).

                Here is the code:\n{self.tokenizer.convert_tokens_to_string(chunk)}\n
                Please return the results in the following format: Label: Count.
                """

                input_ids = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
                with torch.no_grad():
                    output = self.model(input_ids)
                analysis = self.tokenizer.decode(output[0], skip_special_tokens=True)
                results.append(self._parse_analysis(analysis))
            
            final_results = self._aggregate_results(results)
            return final_results
        else:
            return self.analyze_file_single(content, file_type)

    def analyze_file_single(self, content: str, file_type: str) -> Dict[str, Any]:
        # 단일 파일을 분석하는 함수
        prompt = f"""
        You are analyzing a {file_type.upper()} file for potential issues.
        Please list the issues found in the following code related to the following categories:
        1. Redundant Code: Any unnecessary or duplicate code.
        2. Security Vulnerabilities: Any potential exposure of sensitive information or security risks.
        3. High Complexity: Any complex or unoptimized code.
        4. Performance Issues: Any code that may lead to slow performance or inefficiency.
        5. Accessibility Issues: Any issues that could hinder accessibility (for HTML files).
        6. Interactivity Issues: Problems with user interaction or dynamic behavior (for JS files).

        Here is the code:\n{content}\n
        Please return the results in the following format: Label: Count.
        """

        input_ids = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
        with torch.no_grad():
            output = self.model(input_ids)
        
        analysis = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return self._parse_analysis(analysis)

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 여러 분석 결과를 통합하는 함수
        final_results = {
            'Redundant_Code': 1.0,
            'Security_Vulnerability': 1.0,
            'High_Complexity': 1.0,
            'Performance_Issues': 1.0,
            'Accessibility_Issues': 1.0,
            'Interactivity_Issues': 1.0
        }
        
        for result in results:
            for label, score in result.items():
                final_results[label] = min(final_results[label], score)
        
        return final_results

    def _parse_analysis(self, analysis: str) -> Dict[str, Any]:
        # 분석 결과를 파싱하는 함수
        labels = {
            'Redundant_Code': 1.0,
            'Security_Vulnerability': 1.0,
            'High_Complexity': 1.0,
            'Performance_Issues': 1.0,
            'Accessibility_Issues': 1.0,
            'Interactivity_Issues': 1.0
        }

        counts = {}
        for line in analysis.split('\n'):
            match = re.search(r'(\w+):\s*(\d+)', line)
            if match:
                label, count = match.groups()
                counts[label.strip()] = int(count.strip())

        for label in labels.keys():
            if label in counts:
                labels[label] = max(0, 1 - counts[label] * 0.1)
        
        return labels

    def generate_dataset(self) -> pd.DataFrame:
        # 데이터셋을 생성하는 함수
        logging.info("데이터셋 생성 중")
        data = []
        for file in self.collected_files:
            analysis_result = self.analyze_file(file)
            row = {
                'filename': file['name'],
                'file_type': file['type'],
                'code': file['content'],
                'related_files': list(self.link_index.neighbors(file['name']))
            }
            row.update(analysis_result)
            data.append(row)
        return pd.DataFrame(data)

    def generate_review_data(self) -> List[Dict[str, Any]]:
        # 리뷰 데이터를 생성하는 함수
        logging.info("리뷰 데이터 생성 중")
        review_data = []
        for file in self.collected_files:
            analysis_result = self.analyze_file(file)
            for label, score in analysis_result.items():
                if score < 1.0:
                    review_data.append({
                        'filename': file['name'],
                        'file_type': file['type'],
                        'related_files': list(self.link_index.neighbors(file['name'])),
                        'issue_label': label,
                        'code_snippet': self._get_code_snippet(file['content']),
                        'severity': 1 - score,
                        'description': f"Potential {label} issue detected"
                    })
        return review_data

    def _get_code_snippet(self, content: str, length: int = 100) -> str:
        # 코드 스니펫을 가져오는 함수
        return content[:length] + "..." if len(content) > length else content

    def save_dataset(self, dataset: pd.DataFrame, path: str):
        # 데이터셋을 저장하는 함수
        logging.info(f"데이터셋 저장 중: {path}")
        dataset.to_csv(path, index=False, encoding='utf-8-sig')

    def save_review_data(self, review_data: List[Dict[str, Any]], path: str):
        # 리뷰 데이터를 저장하는 함수
        logging.info(f"리뷰 데이터 저장 중: {path}")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(review_data, f, ensure_ascii=False, indent=2)

def main():
    # 메인 함수: 프로그램의 시작점입니다.
    base_url = "https://www.gov.kr/portal/main/nologin"  # 분석할 웹사이트 URL
    crawler = CodeCrawler(base_url)  # CodeCrawler 객체를 생성합니다.
    crawler.collect_files()  # 파일을 수집합니다.
    crawler.create_link_index()  # 링크 인덱스를 생성합니다.

    dataset = crawler.generate_dataset()  # 데이터셋을 생성합니다.
    review_data = crawler.generate_review_data()  # 리뷰 데이터를 생성합니다.

    crawler.save_dataset(dataset, "dataset.csv")  # 데이터셋을 CSV 파일로 저장합니다.
    crawler.save_review_data(review_data, "review_data.json")  # 리뷰 데이터를 JSON 파일로 저장합니다.

if __name__ == "__main__":
    main()  # 메인 함수를 실행합니다.