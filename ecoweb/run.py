from app import create_app
from flask import session
from config import Config
from flask_mongoengine import MongoEngine

app = create_app()
app.secret_key = Config.SECRET_KEY
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'ecoweb',
    'host': 'mongodb://localhost:27017/ecoweb'
}
db = MongoEngine()
db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)  # debug=True로 설정하면 코드 수정 시 자동으로 서버가 재시작됩니다.