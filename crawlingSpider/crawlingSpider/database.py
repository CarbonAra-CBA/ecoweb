from pymongo import MongoClient
import logging

import scrapy

def connect_to_database():
    global client, db, website_collection , traffic_collection
    # MongoDB 서버에 연결
    logging.info("Connecting to MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")

    # 데이터베이스 선택 (예: 'mydatabase'라는 이름의 데이터베이스)
    db = client["ecoweb"]

    # 컬렉션 선택 (예: 'mycollection'이라는 이름의 컬렉션)
    website_collection = db["websites"]
    traffic_collection = db["traffic"]
    logging.info("Connected to MongoDB")

# # 샘플 데이터 삽입
# data = {"name": "John", "age": 30, "city": "New York"}
# collection.insert_one(data)

# # 데이터 조회
# for document in collection.find():
#     print(document)


def disconnect_from_database():
    # MongoDB 연결 종료
    client.close()


def save_to_database_website(website_data):
    logging.info(f"Saving data to database: {website_data['file_name']}")
    website_collection.insert_one(website_data)
    



def save_to_database_traffic(traffic_data):
    logging.info(f"Saving data to database: {traffic_data['url']}")
    traffic_collection.insert_one(traffic_data)  # MongoDB가 `_id`를 자동으로 생성
