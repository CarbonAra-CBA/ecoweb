import requests
from urllib.parse import urlparse
import os

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
    """
    MongoDB에서 가져온 HTML과 CSS를 파일로 저장하고 스크린샷 테스트를 위한 함수
    """
    try:
        # URL에서 도메인 추출
        parsed_url = urlparse(html_file_link['url']) 
        domain = parsed_url.netloc

        # 기본 디렉토리 경로 설정
        base_static_path = f'static/llama/{domain}'
        base_templates_path = f'templates/llama/{domain}'

        # 디렉토리 생성
        os.makedirs(base_static_path, exist_ok=True)
        os.makedirs(base_templates_path, exist_ok=True)

        # HTML 콘텐츠 가져오기
        html_content = fetch_resource_content(html_file_link['url'])
        if not html_content:
            raise Exception(f"Failed to fetch HTML content from {html_file_link['url']}")
        
        # CSS 파일 저장 및 경로 매핑
        css_paths = {}
        # MongoDB cursor를 리스트로 변환
        css_files = list(css_files_link)
        
        for css in css_files:
            try:
                css_url = css['url']
                # CSS 콘텐츠 가져오기
                css_content = fetch_resource_content(css_url)
                if not css_content:
                    print(f"Skipping CSS file {css_url}: Failed to fetch content")
                    continue
                # 원본 CSS URL에서 도메인을 제외한 경로 추출

                parsed_css_url = urlparse(css_url)
                relative_path = parsed_css_url.path.lstrip('/')
                
                # 경로가 비어있는 경우 기본값 설정
                if not relative_path:
                    relative_path = f'styles/style_{len(css_paths)}.css'

                # CSS 파일 저장 경로 생성
                css_save_path = os.path.join(base_static_path, relative_path)
                os.makedirs(os.path.dirname(css_save_path), exist_ok=True)

                # CSS 내용 저장
                with open(css_save_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                # 경로 매핑 저장
                css_paths[css_url] = f'/static/llama/{domain}/{relative_path}'
                
                print(f"CSS saved: {css_save_path}")  # 디버깅용
                
            except Exception as e:
                print(f"Error processing CSS file {css_url}: {str(e)}")
                continue


         # HTML 파일에서 CSS 경로 업데이트
        for original_path, new_path in css_paths.items():
            html_content = html_content.replace(original_path, new_path)
        
        # HTML 파일 저장
        html_save_path = os.path.join(base_templates_path, 'index.html')
        with open(html_save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"HTML saved: {html_save_path}")  # 디버깅용

        return {
            'html_path': html_save_path,
            'css_paths': list(css_paths.values())
        }

    except Exception as e:
        print(f"Error in test_html_css_for_selenium_file_screenshot: {str(e)}")
        raise e
