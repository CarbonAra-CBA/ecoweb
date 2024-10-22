from flask import Flask
# from config import Config

mongo = PyMongo()

# Run 할 시 이것부터 create_app 함수부터 실행됨.
def create_app():

    app = Flask(__name__) # __name__ 은 최외곽 폴더인 Eco-Web 이라는 모듈명을 의미한다.
    # app config 
    # app.config.from_object(Config)
    with app.app_context():
        from . import routes  # routes.py 가져오기


    return app