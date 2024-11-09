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
import os
import json
from flask import session
client, db, collection_traffic, collection_resource = db_connect()

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':    
            url = request.form['wgd-cc-url']
            
            # 1) Lighthouse 실행 
            run_lighthouse(url)
            view_data = process_report(url,collection_resource,collection_traffic) # result 화면에서 사용할 웹사이트에 대한 트래픽 평가 결과
            
            print("view_data first: ", view_data)
            # 2) before(원본) 스크린샷
            capture_screenshot(url, 'app/static/screenshots/before.png', is_file=False)

            # 3) LLAMA로부터 최적화된 코드 받기 (예시)
            try: 
                resource_doc = collection_resource.find_one({'url': url})
                if not resource_doc:
                    raise Exception("Resource document not found in database")
                
                document_requests = [ 
                    req for req in resource_doc['network_requests'] 
                    if req['resourceType'] == 'Document'
                ]

                if not document_requests:
                    raise Exception("HTML document not found in network requests")
                
                # 가장 큰 크기의 HTML 문서 찾기
                html_request = max(
                    document_requests,
                    key=lambda x: x.get('resourceSize', 0)
                )
                html_request_url = html_request['url']

                css_files_link = [
                    req for req in resource_doc['network_requests'] 
                    if req['resourceType'] == 'Stylesheet'
                ]

                # JavaScript 파일들 찾기
                js_files_link = [
                    req for req in resource_doc['network_requests'] 
                    if req['resourceType'] == 'Script'
                ]
                total_byte_weight = view_data['total_byte_weight'] / 1024 # OK.
                print("total_byte_weight: ", total_byte_weight)

                # session Data 저장 
                grade = grade_point(total_byte_weight)
                session['url'] = url
                session['view_data'] = json.dumps(view_data)
                session['grade'] = grade
                return redirect(url_for('result', url=url, grade=grade, view_data=json.dumps(view_data)))

            except Exception as e:
                print(f"Error processing optimized files: {str(e)}")
                return "Error processing files", 500

        return render_template('index.html')
    
    @app.route('/result')
    def result():
        url = request.args.get('url')
        grade = request.args.get('grade')
        view_data_str = request.args.get('view_data')
        grade_s = session.get('grade')
        url_s = session.get('url')
        try:
            # view_data가 URL 파라미터로 전달된 경우
            if view_data_str:
                view_data = json.loads(view_data_str)
                print("view_data_on url:")
            # view_data가 세션에 있는 경우
            elif session.get('view_data'):
                view_data = json.loads(session.get('view_data'))
                print("view_data_on session:")
            # 둘 다 없는 경우
            else:
                return redirect(url_for('home'))
            
            # 탄소 배출량 계산
            kb_weight = view_data['total_byte_weight'] / 1024  # bytes to KB
            carbon_emission = (kb_weight * 0.04) / 272.51
            carbon_emission = round(carbon_emission, 3)
            
            # MB 단위로 변환하여 평균과 비교
            mb_weight = kb_weight / 1024
            global_avg_diff = round(mb_weight - 2.4, 2)
            korea_avg_diff = round(mb_weight - 4.7, 2)
            
            # 성공적으로 데이터를 가져왔으면 세션에 저장
            session['view_data'] = json.dumps(view_data)

            # institution_type 조회 및 예외 처리
            traffic_doc = collection_traffic.find_one({'url': url})
            if traffic_doc and 'institution_type' in traffic_doc:
                institution_type = traffic_doc['institution_type']
            else:
                institution_type = "공공기관"  # 기본값 설정
                print(f"Institution type not found for URL: {url}")
            session['institution_type'] = institution_type

            
            return render_template('result.html', 
                                url=url_s, 
                                grade=grade_s,
                                view_data=view_data, 
                                kb_weight=kb_weight,
                                carbon_emission=carbon_emission,
                                global_avg_diff=global_avg_diff,
                                korea_avg_diff=korea_avg_diff,
                                institution_type=institution_type)
                                
        except Exception as e:
            print(f"Error in result route: {str(e)}")
            return redirect(url_for('home'))
        
    @app.route('/login')
    def login():
        return render_template('login.html')