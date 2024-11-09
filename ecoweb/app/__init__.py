from flask import Flask
from config import Config
from app.database import MongoDB

db = MongoDB()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # MongoDB 초기화
    db.init_app(app)
    
    # 라우트 등록
    from . import routes
    routes.init_routes(app)
    
    return app