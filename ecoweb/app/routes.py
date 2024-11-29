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
from app.ProjectMaker.DirectoryMaker import directory_maker, directory_to_json
from app.ProjectMaker.guideline_report import create_guideline_report, guideline_summarize
from dotenv import load_dotenv
import re
from app.Image_Classification import model_test, png2webp
from app.lighthouse import process_urls as proc_url
import urllib.request
import os
import requests
import zipfile
from io import BytesIO, StringIO
from flask import send_file
import shutil
<<<<<<< HEAD
from flask import send_from_directory, current_app
=======
from app.ProjectMaker.code_optimizer import code_optimizer, getCodeSize_before, getCodeSize_after

ZIP_FILE_PATH = "/"
>>>>>>> upstream/main

load_dotenv()
# 가이드라인 분석 결과를 임시 저장할 딕셔너리
guideline_results = {}

def perform_async_guideline_analize(task_id, url_s, root_path):
    # 디렉토리 생성 및 가이드라인 분석 수행

    print("directory make success. root path:", root_path)

    # 가이드라인 분석 결과 생성
    answer_list = create_guideline_report(project_root_path=root_path)
    guideline_list = guideline_summarize(answer_list=answer_list)

    # 결과를 async_results에 저장
    guideline_results[task_id] = guideline_list

def init_routes(app):

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
                print("Error creating user: {}".format(str(e)))
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
            # capture_screenshot(url, 'app/static/screenshots/before.png', is_file=False)

            try:
                total_byte_weight = view_data['total_byte_weight'] / 1024  # OK.
                print("total_byte_weight: ", total_byte_weight)

                # session Data 저장
                grade = grade_point(total_byte_weight)
                session['url'] = url
                session['view_data'] = json.dumps(view_data)
                session['grade'] = grade
                return redirect(url_for('carbon_calculate_emission'))

            except Exception as e:
                print("Error processing optimized files: {}".format(str(e)))
                return "Error processing files", 500
        if request.method == 'GET':
            return render_template('main.html')

    @app.route('/carbon_calculate_emission')
    def carbon_calculate_emission():
        print("Entering carbon_calculate_emission route")  # 디버깅 로그
        
        if not session.get('url'):
            flash('먼저 홈페이지에서 URL을 입력해주세요.', 'warning')
            return redirect(url_for('home'))
        
        try:
            url = session.get('url')

            # 세션에서 데이터 가져오기
            traffic_doc = db.db.lighthouse_traffic.find_one({'url': url})
            institution_type = traffic_doc.get('institution_type', '공공기관') if traffic_doc else '공공기관'
            session['institution_type'] = institution_type

            view_data = json.loads(session.get('view_data'))
            grade = session.get('grade')
            kb_weight = view_data['total_byte_weight'] / 1024
            session['kb_weight'] = kb_weight
            # 탄소 배출량 계산 (0.04 kWh/GB * 442g CO2/kWh)
            carbon_emission = round((kb_weight * 0.04) / 272.51, 3)
            # MB로 변환하여 평균과 비교
            mb_weight = kb_weight / 1024
            global_avg_diff = round(mb_weight - 2.4, 2)  # 세계 평균 2.4MB 기준
            session['global_avg_carbon'] = 0.36
            korea_avg_diff = round(mb_weight - 4.7, 2)   # 한국 평균 4.7MB 기준
            session['korea_avg_carbon'] = 0.70
            session['carbon_emission'] = carbon_emission
            korea_diff = session['korea_avg_carbon'] - carbon_emission
            korea_diff_abs = abs(round(korea_diff, 2))
            global_diff = session['global_avg_carbon'] - carbon_emission
            global_diff_abs = abs(round(global_diff, 2))
            session['global_diff'] = global_diff
            session['korea_diff'] = korea_diff
            session['global_diff_abs'] = global_diff_abs
            session['korea_diff_abs'] = korea_diff_abs
            print("Rendering template with data - carbon_emission: {}, grade: {}".format(carbon_emission, grade))
            
            return render_template('carbon_calculate_emission.html',
                                url=url,
                                view_data=view_data,
                                grade=grade,
                                carbon_emission=carbon_emission,
                                global_avg_diff=global_avg_diff,
                                korea_avg_diff=korea_avg_diff,
                                global_avg_carbon=session['global_avg_carbon'],
                                korea_avg_carbon=session['korea_avg_carbon'],
                                kb_weight=kb_weight,
                                korea_diff=korea_diff,
                                global_diff=global_diff,
                                korea_diff_abs=korea_diff_abs,
                                global_diff_abs=global_diff_abs,
                                institution_type=institution_type,
                                analysis_date=datetime.now())
                                
        except Exception as e:
            print("Error in carbon_calculate_emission: {}".format(str(e)))  # 디버깅 로그
            flash('세션이 만료되었거나 오류가 발생했습니다.', 'error')
            return redirect(url_for('home'))

    @app.route('/gov-analysis')
    def gov_analysis():
        global_avg_carbon = session.get('global_avg_carbon')    
        korea_avg_carbon = session.get('korea_avg_carbon')

        carbon_emission = session.get('carbon_emission')
        # 현재 탄소배출량은 글로벌 평균에 비해 n% 높다.
        global_diff = session.get('global_diff')
        korea_diff = session.get('korea_diff')
        global_diff_abs = session.get('global_diff_abs')
        korea_diff_abs = session.get('korea_diff_abs')
        return render_template('gov_analysis.html', 
                               global_avg_carbon=global_avg_carbon,
                               korea_avg_carbon=korea_avg_carbon,
                               carbon_emission=carbon_emission,
                               global_diff=global_diff,
                               korea_diff=korea_diff,
                               global_diff_abs=global_diff_abs,
                               korea_diff_abs=korea_diff_abs)
        
    @app.route('/code_optimization')
    def code_optimization():
        view_data = session.get('view_data')
        url_s = session.get('url')

        print("[view_data] : ", view_data)
        # JSON 문자열을 딕셔너리로 변환
        try:
            view_data = json.loads(view_data) if view_data else {}
        except:
            view_data = {}

        # print("[view_data-after] : ", view_data)
        collection_traffic = db.db.lighthouse_traffic
        collection_resource = db.db.lighthouse_resource

        root_path = directory_maker(url=url_s, collection_traffic=collection_traffic,
                                        collection_resource=collection_resource)
        
        # 비동기 작업(가이드라인 분석)
        task_id = str(uuid.uuid4())
        thread = Thread(target=perform_async_guideline_analize, args=(task_id, url_s, root_path))
        thread.start()
        # 코드 최적화 결과 수집
        # 파일 구조를 json으로 표현해서 전달
        directory_structure = directory_to_json(root_path)
        print("Directory Structure : ")
        print(type(directory_structure))
        print(directory_structure)
        # 각 리소스 원본 크기와 줄어든 크기를 전달
        result = getCodeSize_before(root_path)
        print('before', result)
        # 웹 프로젝트 압축 버전을 다운로드할 수 있게 제공하기
        ZIP_FILE_PATH = code_optimizer(root_path)
        result = getCodeSize_after(root_path, result)
        print('after', result)
        
        return render_template('code_optimization.html', 
                               view_data=view_data,
                               task_id = task_id,
                               directory_structure=directory_structure,
                               resource_size=result)
    
    @app.route('/img_optimization')
    def img_optimization():
        url_s = session.get('url')
        if "https://" in url_s:
            url_s = url_s.replace("https://", "")
        print("url_s : ", url_s)
        # 이미지 분류
        Image_paths = proc_url.get_report_imagepath()
        # 이거 gitingnore 하세요. 
        image_dir_path = f'app/static/images/{url_s}'
        if os.path.exists(image_dir_path):
            shutil.rmtree(image_dir_path)

        os.makedirs(image_dir_path)

        files = []
        for imageurl in Image_paths:
            try:
                spliturl = re.split(r':|\/|\.', imageurl)
                filename = spliturl[-2] + '.' + spliturl[-1]
                destination = os.path.join(image_dir_path, filename)
                response = requests.get(imageurl, verify=False)
    
                # 성공적으로 다운로드된 경우에만 파일 저장
                if response.status_code == 200:
                    with open(destination, 'wb') as f:
                        f.write(response.content)
                    print(f"다운로드 성공: {filename}")
                    files.append(model_test.predict_image(destination, filename, f'app/static/images/{url_s}/results')) # url별로 경로 생성
                else:
                    print(f"다운로드 실패: {filename}(상태코드 : {response.status_code})")
            except Exception as e:
                print("download error : {}".format(e))

        category = {
            'iconfile': [],
            'logofile': [],
            'others': []
        }

        webpfiles = []
        count = 0
        totalsize = 0
        for file in files:
            if file['class_name'] == 'jpg_svg' or file['class_name'] == 'jpg_logo':
                webpfiles.append(file)
                count += 1
                totalsize += file['size']
                if "ico" in file['name']:
                    category['iconfile'].append(file)
                elif "logo" in file['name']:
                    category['logofile'].append(file)
                else:
                    category['others'].append(file)

        # webp 변환
        convertedfiles = []
        convertedfiles = png2webp.main()
        convertedfiles.sort(key=lambda x: x['name'], reverse=True)
        webpfiles.sort(key=lambda x: x['name'], reverse=True)

        # viewdata

        view_data = session.get('view_data')
        # JSON 문자열을 딕셔너리로 변환
        try:
            view_data = json.loads(view_data) if view_data else {}
        except:
            view_data = {}
        return render_template('img_optimization.html',
                            category=category,   
                            files=webpfiles, 
                            convertedfiles=convertedfiles,
                            filecount=count,
                            totalsize=totalsize,
                            view_data=view_data,
                            url_s=url_s)

    @app.route('/world_analysis')
    def world_analysis():
        return render_template('world_analysis.html')
    

    # 다운로드 zip파일
    @app.route('/download-webp')
    def download_webp():
        url_s = session.get('url')
        if "https://" in url_s:
            url_s = url_s.replace("https://", "")
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            webp_dir = os.path.join('app/static/images', url_s, 'img_to_webp')
            # webp 파일들을 찾아서 ZIP 파일에 추가
            for root, dirs, files in os.walk(webp_dir):
                for file in files:
                    if file.endswith('.webp'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, webp_dir)
                        zf.write(file_path, arcname)
    
        # 파일 포인터를 처음으로 되돌림
        memory_file.seek(0)

        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name='converted_webp_files.zip'
        )
    
    @app.route('/download-single-webp/<path:url_s>/<filename>')
    def download_single_webp(url_s, filename):
        try:
            # url_s에서 http:// 또는 https:// 제거
            url_s = url_s.replace('http://', '').replace('https://', '')
            
            # 파일 경로 설정
            webp_folder = os.path.join(current_app.static_folder, 'images', url_s, 'img_to_webp')
            webp_file = os.path.join(webp_folder, filename)
            
            print(f"Attempting to download file: {webp_file}")  # 디버깅용
            
            if not os.path.exists(webp_file):
                print(f"File not found: {webp_file}")  # 디버깅용
                return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
                
            # 파일 이름에서 확장자가 없는 경우 .webp 추가
            if not filename.lower().endswith('.webp'):
                filename = f"{filename}.webp"
                
            return send_from_directory(
                webp_folder,
                filename,
                as_attachment=True,
                mimetype='image/webp'
            )
            
        except Exception as e:
            print(f"Error downloading file: {str(e)}")  # 디버깅용
            return jsonify({'error': '파일 다운로드 중 오류가 발생했습니다.'}), 500

    @app.route('/download_code')
    def download_zip():
        try:
            # ZIP 파일을 전송
            return send_file(ZIP_FILE_PATH, as_attachment=True)
        except Exception as e:
            return str(e)

    if __name__ == '__main__':
        app.run(debug=True)
