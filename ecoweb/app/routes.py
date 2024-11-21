from threading import Thread
import uuid

from flask import render_template, request, redirect, url_for
from app.utils.grade import (grade_point)
from app.services.screenshot import capture_screenshot
from app.services.lighthouse import run_lighthouse
from app.services.lighthouse import process_report
import json
from flask import session
from app.models import User, Institution
from flask import flash
from app import db
from werkzeug.security import generate_password_hash, check_password_hash  # check_password_hash 추가
from datetime import datetime
from flask import jsonify
from flask import g

from app.ProjectMaker.DirectoryMaker import directory_maker
from app.ProjectMaker.guideline_report import create_guideline_report, guideline_summarize
from dotenv import load_dotenv

import re
from app.Image_Classification import model_test
from app.lighthouse import process_urls as proc_url
import urllib.request
import os


load_dotenv()
# 가이드라인 분석 결과를 임시 저장할 딕셔너리
guideline_results = {}

def perform_async_guideline_analize(task_id, url_s, collection_traffic, collection_resource):
    # 디렉토리 생성 및 가이드라인 분석 수행
    root_path = directory_maker(url=url_s, collection_traffic=collection_traffic,
                                        collection_resource=collection_resource)
    print("directory make success. root path:", root_path)

    # 가이드라인 분석 결과 생성
    answer_list = create_guideline_report(project_root_path=root_path)
    guideline_list = guideline_summarize(answer_list=answer_list)


    # 결과를 async_results에 저장
    guideline_results[task_id] = guideline_list

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            url = request.form['wgd-cc-url']

            # 1) Lighthouse 실행
            run_lighthouse(url)
            # MongoDB 컬렉션 가져오기
            collection_traffic = db.db.lighthouse_traffic
            collection_resource = db.db.lighthouse_resource
            view_data = process_report(url, collection_resource,
                                       collection_traffic)  # result 화면에서 사용할 웹사이트에 대한 트래픽 평가 결과

            print("view_data first: ", view_data)
            # 만약, viewdata의 total_byte_weight이 0이라면 예외처리 (error.html 페이지로 리다이렉트)
            if view_data['total_byte_weight'] == 0:
                return redirect(url_for('error'))
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
                total_byte_weight = view_data['total_byte_weight'] / 1024  # OK.
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
        if request.method == 'GET':
            return render_template('main.html')


    @app.route('/result')
    def result():
        url = request.args.get('url')
        grade = request.args.get('grade')
        view_data_str = request.args.get('view_data')
        grade_s = session.get('grade')
        url_s = session.get('url')

        collection_traffic = db.db.lighthouse_traffic
        collection_resource = db.db.lighthouse_resource

        try:
            # view_data 처리
            if view_data_str:
                view_data = json.loads(view_data_str)
                print("view_data_on url:")
            elif session.get('view_data'):
                view_data = json.loads(session.get('view_data'))
                print("view_data_on session:")
            else:
                return redirect(url_for('/'))

            # 탄소 배출량 및 기타 정보 계산
            kb_weight = view_data['total_byte_weight'] / 1024  # bytes to KB
            carbon_emission = round((kb_weight * 0.04) / 272.51, 3)
            mb_weight = kb_weight / 1024
            global_avg_diff = round(mb_weight - 2.4, 2)
            korea_avg_diff = round(mb_weight - 4.7, 2)

            # 세션에 view_data 저장
            session['view_data'] = json.dumps(view_data)

            # institution_type 조회
            traffic_doc = db.db.lighthouse_traffic.find_one({'url': url})
            institution_type = traffic_doc.get('institution_type', '공공기관') if traffic_doc else '공공기관'
            session['institution_type'] = institution_type

            # 비동기 작업(가이드라인 분석)
            task_id = str(uuid.uuid4())
            thread = Thread(target=perform_async_guideline_analize, args=(task_id, url_s, collection_traffic, collection_resource))
            thread.start()

            # 이미지 분류
            Image_paths = proc_url.get_report_imagepath()

            image_dir_path = 'C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/Github/ecoweb/ecoweb/app/images'
            if not os.path.exists(image_dir_path):
                os.mkdir(image_dir_path)

            files = []
            for imageurl in Image_paths:
                try:
                    spliturl = re.split(r':|\/|\.', imageurl)
                    filename = spliturl[-2] + '.' + spliturl[-1]
                    destination = os.path.join(image_dir_path, filename)
                    urllib.request.urlretrieve(imageurl, destination)
                    files.append(model_test.predict_image(destination, filename, 'C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/Github/ecoweb/ecoweb/app/images/results'))
                except Exception as e:
                    print(f"download error : {e}")

            category = {
                'iconfile': [],
                'logofile': [],
                'others': []
            }
            svgfiles = []
            count = 0
            totalsize = 0
            for file in files:
                if file['class_name'] == 'jpg_svg' or file['class_name'] == 'jpg_logo':
                    svgfiles.append(file)
                    count += 1
                    totalsize += file['size']
                    if "ico" in file['name']:
                        category['iconfile'].append(file)
                    elif "logo" in file['name']:
                        category['logofile'].append(file)
                    else:
                        category['others'].append(file)


            return render_template('result.html',
                                   url=url_s,
                                   grade=grade_s,
                                   view_data=view_data,
                                   kb_weight=kb_weight,
                                   carbon_emission=carbon_emission,
                                   global_avg_diff=global_avg_diff,
                                   korea_avg_diff=korea_avg_diff,
                                   institution_type=institution_type,
                                   guideline_list=guideline_results,
                                   task_id=task_id,
                                   files=svgfiles,
                                   category=category,
                                   filecount=count,
                                   totalsize=totalsize
                                   )

        except Exception as e:
            print(f"Error in result route: {str(e)}")
            return redirect(url_for('/'))

    @app.route('/check_async/<task_id>', methods=['GET'])
    def check_async(task_id):
        """
        비동기 작업의 상태를 확인하는 엔드포인트.
        """
        if task_id in guideline_results:
            result = guideline_results.pop(task_id)  # 결과 가져오고 제거
            return jsonify({'status': 'completed', 'result': result})
        else:
            # 비동기 작업이 아직 완료되지 않았음
            return jsonify({'status': 'pending'}), 202  # 202 Accepted

    @app.route('/login', methods=['GET', 'POST'])  # methods=['GET', 'POST'] 추가 필요
    def login():
        if request.method == 'POST':
            # 로그인 처리
            username = request.form['username']
            password = request.form['password']
            # hash 디코딩
            login_user = db.db.users.find_one({'username': username})

            if login_user and check_password_hash(login_user['password'], password):
                flash('로그인이 완료되었습니다!', 'success')

                db.db.users.update_one(
                    {'username': username},
                    {'$set': {'last_login': datetime.now()}}
                )

                session['user_id'] = str(login_user['_id'])  # 세션에 사용자 ID 저장
                session['username'] = login_user['username']
                session['department'] = login_user['department']  # 부서 정보 추가
                session['institution'] = login_user['institution']['name']  # 기관 정보 추가

                return redirect(url_for('home'))
            else:
                # 로그인 실패
                flash('아이디 또는 비밀번호가 일치하지 않습니다.', 'error')
                return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            # 아아디 중복 확인
            if db.db.users.find_one({'username': request.form['username']}):
                flash('이미 존재하는 아이디입니다.', 'error')
                return redirect(url_for('signup'))

            # 기관 정보 생성
            institution = Institution(
                name=request.form['institution_name'],
                type=request.form['institution_type'],
                website_url=request.form['institution_website_url']
            )

            # 사용자 정보 생성
            user = User(
                username=request.form['username'],
                password=generate_password_hash(request.form['password']),
                name=request.form['name'],
                email=request.form['email'],
                phone=request.form['phone'],
                department=request.form['department'],
                position=request.form['position'],
                institution=institution.to_dict()
            )

            try:
                # MongoDB에 저장
                result = db.db.users.insert_one(user.to_dict())
                print("Inserted document ID:", result.inserted_id)  # 삽입된 문서 ID 출력
                flash('회원가입이 완료되었습니다!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                print(f"Error creating user: {str(e)}")
                flash('회원가입 중 오류가 발생했습니다.', 'error')
                return redirect(url_for('signup'))

        return render_template('signup.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('로그아웃이 완료되었습니다!', 'success')
        return redirect(url_for('home'))

    @app.route('/api/badge')
    def badge_data():
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400

        try:
            # MongoDB에서 데이터 조회
            data = db.db.lighthouse_resource.find_one({'url': url})
            if not data:
                return jsonify({'error': 'URL not found'}), 404

            # 탄소 배출량 계산
            kb_weight = data['total_byte_weight'] / 1024
            carbon = round((kb_weight * 0.04) / 272.51, 3)

            # 백분위 계산 (다른 사이트들과 비교)
            all_sites = list(db.db.lighthouse_resource.find())
            better_than = sum(1 for site in all_sites
                              if site['total_byte_weight'] > data['total_byte_weight'])
            percentage = round((better_than / len(all_sites)) * 100)

            return jsonify({
                'carbon': carbon,
                'percentage': percentage
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/badge')
    def badge():
        return render_template('badge.html')

    @app.route('/error')
    def error():
        return render_template('error.html')

    # @app.route('/newresult')
    # def newresult():
    #     return render_template('newresult.html')
