from flask import Flask
from flask import session
from flask_mongoengine import MongoEngine

def create_app():
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        'db': 'ecoweb',
        'host': 'mongodb://localhost:27017/ecoweb'
    }
    db = MongoEngine()
    db.init_app(app)
    # 디버그모드 on
    with app.app_context():
        from . import routes
        routes.init_routes(app)
        
    return app