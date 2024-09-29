# debug mode
import base64
import os


# log 정도 설정

BASE_DIR = os.path.dirname(__file__)

class Config:
    # mongodb config
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/mydatabase')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
