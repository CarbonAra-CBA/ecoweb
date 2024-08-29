from flask import (
    Blueprint, render_template,json, request, redirect, url_for
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crawlingSpider.crawlingSpider.driver import Driver
from crawlingSpider.crawlingSpider.traffic import trafficSpider
from utils.grade import grade_point

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

bp = Blueprint('main', __name__, url_prefix='/') # main 이라는 블루프린트 이름을 가지고, url_prefix 는 / 이다.
# 즉, / 로 시작하는 url은 main 블루프린트에 등록된 함수로 연결된다. (result() 함수면 result로 등록된다.

@bp.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        print(f"Calculate Carbon footprint for: {url}")
        driver = Driver().init_driver()
        # 해당 페이지만 크롤링
        traffic_data = trafficSpider.crawling_items(url, driver)
        print("total_size_of_URL", traffic_data['total_size'])  # 여기서 total_size에 딕셔너리 스타일로 접근

        # 해당 페이지 등급평가
        grade = grade_point(traffic_data['total_size'])

        return redirect(url_for('main.result', url=url, grade=grade)) # main.result 는 result 함수 이름을 엔드포인트로 갖는것을 의미함.

    return render_template('index.html')

@bp.route('/result')
def result():
    url = request.args.get('url')
    grade = request.args.get('grade')
    return render_template('result.html', url=url, grade=grade)
