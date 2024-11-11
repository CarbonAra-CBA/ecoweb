import requests
from urllib.parse import urlparse
import os
import time
def fetch_resource_content(url):
    """URL로부터 리소스 콘텐츠를 가져오는 함수"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 4XX, 5XX 에러 체크
        return response.text
    except Exception as e:
        print(f"Error fetching content from {url}: {str(e)}")
        return None
    
def test_html_css_for_selenium_file_screenshot(html_file_link, css_files_link, js_files_link):
    try:
        # URL에서 도메인 추출
        parsed_url = urlparse(html_file_link) 
        domain = parsed_url.netloc
        base_path = os.path.join('llama', domain)

        # CSS 파일 저장 및 경로 매핑
        css_paths = {}
        for css in css_files_link:
            try:
                css_url = css['url']
                css_content = fetch_resource_content(css_url)
                if not css_content:
                    continue

                # 원본 URL에서 경로 구조 추출
                parsed_css_url = urlparse(css_url)
                css_path = parsed_css_url.path.lstrip('/')  # 앞의 '/' 제거
                
                if not css_path:  # 경로가 비어있는 경우
                    css_path = f'assets/style_{len(css_paths)}.css'
                
                # CSS 파일 저장 경로 생성
                css_save_path = os.path.join(base_path, css_path)
                os.makedirs(os.path.dirname(css_save_path), exist_ok=True)

                with open(css_save_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                # HTML에서 사용할 상대 경로
                # 원본 경로 구조를 유지하되, 도메인 부분만 제거
                css_paths[css_url] = css_path
                
                print(f"CSS saved: {css_save_path}")
                
            except Exception as e:
                print(f"Error processing CSS file {css_url}: {str(e)}")
                continue
        # HTML 콘텐츠 가져오기
        html_content = fetch_resource_content(html_file_link)
        if not html_content:
            raise Exception(f"Failed to fetch HTML content from {html_file_link}")

        # HTML에서 CSS 경로 업데이트
        for original_url, new_path in css_paths.items():
            # 절대 URL을 상대 경로로 변환
            html_content = html_content.replace(original_url, new_path)
            
            # 절대 경로(/로 시작하는)를 상대 경로로 변환
            original_path = urlparse(original_url).path
            if original_path:
                html_content = html_content.replace(f'href="{original_path}"', f'href="{new_path}"')
                html_content = html_content.replace(f"href='{original_path}'", f"href='{new_path}'")

        # HTML 파일 저장
        html_save_path = os.path.join(base_path, 'index.html')
        with open(html_save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"HTML saved: {html_save_path}")
        print("CSS paths mapping:", css_paths)

        return {
            'html_path': html_save_path,
            'css_paths': list(css_paths.values())
        }
    except Exception as e:
        print(f"Error in test_html_css_for_selenium_file_screenshot: {str(e)}")
        return None

