from flask import Flask
from views import main_views
from flask import Flask
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()


# Run 할 시 이것부터 create_app 함수부터 실행됨.
def create_app():

    app = Flask(__name__) # __name__ 은 최외곽 폴더인 Eco-Web 이라는 모듈명을 의미한다.

    # MongoDB 설정
    app.config["MONGO_URI"] = "mongodb://localhost:27017/mydatabase"
    
    # app config 
    app.config.from_object(Config)

    # Initialize MongoDB
    mongo.init_app(app)

    app.register_blueprint(main_views.bp) # main_views.py 에서 정의한 bp 를 등록한다.
    # bp는 Blueprint 객체이다.
    return app