from flask import render_template, request, redirect, url_for
from utils.grade import grade_point
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

from app.ProjectMaker.DirectoryMaker import directory_maker
from app.ProjectMaker.guideline_report import create_guideline_report, guideline_summarize
from dotenv import load_dotenv

load_dotenv()


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
                return redirect(url_for('/'))

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
            traffic_doc = db.db.lighthouse_traffic.find_one({'url': url})
            if traffic_doc and 'institution_type' in traffic_doc:
                institution_type = traffic_doc['institution_type']
            else:
                institution_type = "공공기관"  # 기본값 설정
                print(f"Institution type not found for URL: {url}")
            session['institution_type'] = institution_type

            # 가이드라인 분석
            # root_path = directory_maker(url=url_s, collection_traffic=collection_traffic,
            #                             collection_resource=collection_resource)
            # print("directory make success. root path : ", root_path)
            # answer_list = create_guideline_report(project_root_path=root_path)
            # guideline_list = guideline_summarize(answer_list=answer_list)
            # print(guideline_list)
            guideline_list = []

            return render_template('result.html',
                                   url=url_s,
                                   grade=grade_s,
                                   view_data=view_data,
                                   kb_weight=kb_weight,
                                   carbon_emission=carbon_emission,
                                   global_avg_diff=global_avg_diff,
                                   korea_avg_diff=korea_avg_diff,
                                   institution_type=institution_type,
                                   guideline_list=guideline_list)

        except Exception as e:
            print(f"Error in result route: {str(e)}")
            return redirect(url_for('/'))

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
