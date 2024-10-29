from flask import render_template, request, redirect, url_for
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from utils.grade import grade_point
from utils.file_request import test_html_css_for_selenium_file_screenshot
from app.services.screenshot import capture_screenshot
from app.services.lighthouse import run_lighthouse
from app.services.lighthouse import process_report
from app.services.llama import llama_optimizing_code
from utils.db_con import db_connect

client, db, collection_traffic, collection_resource = db_connect()

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            url = request.form['url']
            
            # 1) Lighthouse 실행 
            run_lighthouse(url)
            view_data = process_report(url,collection_resource,collection_traffic) # result 화면에서 사용할 웹사이트에 대한 트래픽 평가 결과
            # 2) before(원본) 스크린샷
            capture_screenshot(url, 'app/static/screenshots/before.png', is_file=False)

            # 3) LLAMA로부터 최적화된 코드 받기 (예시)
            try: 
                resource_doc = collection_resource.find_one({'url': url})
                if not resource_doc:
                    raise Exception("Resource document not found in database")
                
                # HTML 문서 찾기
                html_request = next(
                    (req for req in resource_doc['network_requests']
                     if req['resourceType'] == 'Document'),
                     None
                )
                if not html_request:
                    raise Exception("HTML document not found in network requests")
                
                css_files_link = [
                    req for req in resource_doc['network_requests'] 
                    if req['resourceType'] == 'Stylesheet'
                ]

                # JavaScript 파일들 찾기
                js_files_link = [
                    req for req in resource_doc['network_requests'] 
                    if req['resourceType'] == 'Script'
                ]
                # 파일 저장 및 스크린샷
                saved_files = test_html_css_for_selenium_file_screenshot(
                    html_request, css_files_link, js_files_link
                )
                # optimized_files = llama_optimizing_code(html_file_link, css_files_link, js_files_link)

                # (일단 아직 LLAMA가 완성되지 않았으니, File selenium이 잘 동작하는지, 임의의 html,css를 넣어서 스크린샷 찍어보자. 
                # 일단 collection_resource 에서 url의 html, css를 똑같이 저장해보자

                # 4) 최적화된 페이지 스크린샷
                after_screenshot_path = 'app/static/screenshots/after.png'
                print("saved_files['html_path']: ", saved_files['html_path'])
                capture_screenshot(saved_files['html_path'], after_screenshot_path, is_file=True)

                print("Screenshots captured successfully")  # 디버깅용
                total_byte_weight = view_data['total_byte_weight'] / 1024
                grade = grade_point(total_byte_weight)
                return redirect(url_for('result', url=url, view_data=view_data, grade=grade))

            except Exception as e:
                print(f"Error processing optimized files: {str(e)}")
                return "Error processing files", 500

        return render_template('index.html')

    @app.route('/result')
    def result():
        url = request.args.get('url')
        grade = request.args.get('grade')
        view_data = request.args.get('view_data')
        return render_template('result.html', url=url, grade=grade)