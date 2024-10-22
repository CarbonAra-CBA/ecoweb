from flask import Flask
# from config import Config

# Run 할 시 이것부터 create_app 함수부터 실행됨.
def create_app():
    app = Flask(__name__)
    
    with app.app_context():
        from . import routes
        routes.init_routes(app)

    return app