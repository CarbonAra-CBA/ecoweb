from flask import Flask
# from config import Config
from flask import session
# Run 할 시 이것부터 create_app 함수부터 실행됨.
def create_app():
    app = Flask(__name__)
    # 디버그모드 on
    with app.app_context():
        from . import routes
        routes.init_routes(app)
        
    return app