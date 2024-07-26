from flask import Flask
import config
from views import main_views

# Run 할 시 이것부터 create_app 함수부터 실행됨.
def create_app():

    app = Flask(__name__) # __name__ 은 최외곽 폴더인 Eco-Web 이라는 모듈명을 의미한다.

    app.config.from_object(config) # 설정 파일을 적용한다.

    app.register_blueprint(main_views.bp) # main_views.py 에서 정의한 bp 를 등록한다.
    # bp는 Blueprint 객체이다.
    return app