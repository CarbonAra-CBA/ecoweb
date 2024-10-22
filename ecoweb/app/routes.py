from flask import render_template
from . import create_app
from crawlingSpider.crawlingSpider.traffic import trafficSpider
from ..utils import grade
from flask import request, redirect, url_for
app = create_app()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        url = request.form.get('url')
        print(f"Calculate Carbon footprint for: {url}")
        driver = Driver().init_driver()
        # 해당 페이지만 크롤링
        traffic_data = trafficSpider.crawling_items(url, driver)
        print("total_size_of_URL", traffic_data['total_size'])  # 여기서 total_size에 딕셔너리 스타일로 접근

        # 해당 페이지 등급평가
        url_grade = grade.grade_point(traffic_data['total_size'])

        return redirect(url_for('main.result', url=url, grade=url_grade)) # main.result 는 result 함수 이름을 엔드포인트로 갖는것을 의미함.

    return render_template('index.html')

@bp.route('/result')
def result():
    url = request.args.get('url')
    grade = request.args.get('grade')
    return render_template('result.html', url=url, grade=grade)