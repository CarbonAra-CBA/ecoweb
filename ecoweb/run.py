from app import create_app
from flask import session
from flask import Flask
from app import create_app, db
from config import Config

app = create_app()
app.secret_key = Config.SECRET_KEY

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        db.close()  # 애플리케이션 종료 시 연결 닫기