from urllib.parse import urljoin, urlparse
import os


# 아직 LLAMA code 작성 안 했음.(추후 작성)
def LLAMAexecute(html_link,css_link,js_link):
    # LLAMA의 응답이 자연어로 리턴됩니다. 
    return 1,2,3,4 

def llama_optimizing_code(html_file_link, css_files_link, js_files_link):
                """
                LLAMA로부터 받은 최적화된 코드를 저장하고 경로를 구성하는 함수
                """
                # LLAMA 실행 및 최적화된 코드 받기   
                html_file, css_files, js_files,report = LLAMAexecute(html_file_link, css_files_link, js_files_link)
                

                # URL에서 도메인 추출
                parsed_url = urlparse(html_file_link['url']) 
                domain = parsed_url.netloc

                # 기본 디렉토리 경로 설정
                base_static_path = f'static/llama/{domain}'
                base_templates_path = f'templates/llama/{domain}'

                # 디렉토리 생성
                os.makedirs(base_static_path, exist_ok=True)
                os.makedirs(base_templates_path, exist_ok=True)

                # CSS 파일 저장 및 경로 매핑
                css_paths = {}

                # 일단 LLAMAexecute는 구현이 안 되었으니, 테스트용 html_file ,css_files 사용하겠음 (js는 스크린샷에 영향 안주니까 사용 X)
                # css의 "url"에서 현재 url 부분을 제외한다.
                for css in css_files: 

                    # 원본 CSS URL에서 도메인을 제외한 경로 추출
                    css_url = css['url']
                    parsed_css_url = urlparse(css_url)
                    relative_path = parsed_css_url.path.lstrip('/')

                    # CSS 파일 저장 경로 생성
                    css_save_path = os.path.join(base_static_path, relative_path)
                    os.makedirs(os.path.dirname(css_save_path), exist_ok=True)  

                    # CSS 내용 저장
                    with open(css_save_path, 'w', encoding='utf-8') as f:
                        f.write(css['content'])
                    
                    # 경로 매핑 저장
                    css_paths[css_url] = f'/static/llama/{domain}/{relative_path}'
                
                    # HTML 파일에서 CSS 경로 업데이트
                    html_content = html_file['content']
                    for original_path, new_path in css_paths.items():
                        html_content = html_content.replace(original_path, new_path)
                    
                    # HTML 파일 저장
                    html_save_path = os.path.join(base_templates_path, 'index.html')
                    with open(html_save_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    return {
                        'html_path': html_save_path,
                        'css_paths': list(css_paths.values()),
                        'report': report
                    }