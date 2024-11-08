from app import create_app
from flask import session
from config import Config
app = create_app()
app.secret_key = Config.SECRET_KEY
if __name__ == '__main__':
    app.run(debug=True)  # debug=True로 설정하면 코드 수정 시 자동으로 서버가 재시작됩니다.