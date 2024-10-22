from flask import render_template, request, redirect, url_for
from crawlingSpider.traffic import trafficSpider
from utils import grade
from crawlingSpider.database import find_url_in_database

def init_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def home():
        if request.method == 'POST':
            url = request.form.get('url')
            print(f"Calculate Carbon footprint for: {url}")
            
            # DB에 url 존재하면, 찾아서 크롤링 안 함 
            if find_url_in_database(url):
                print("url already exists in database")
                url_total_size = find_url_in_database(url)[1]['total_size']
                url_grade = grade.grade_point(url_total_size)
                return redirect(url_for('result', url=url, grade=url_grade))
            # 없으면 크롤링  
            else: 
                # 해당 페이지만 크롤링
                traffic_spider = trafficSpider()
                traffic_data = traffic_spider.crawling_items(url)
                print("total_size_of_URL", traffic_data['total_size'])
                # 해당 페이지 등급평가
                url_grade = grade.grade_point(traffic_data['total_size'])

                return redirect(url_for('result', url=url, grade=url_grade))

        return render_template('index.html')

    @app.route('/result')
    def result():
        url = request.args.get('url')
        grade = request.args.get('grade')
        return render_template('result.html', url=url, grade=grade)