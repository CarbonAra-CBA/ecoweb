from pymongo import MongoClient
import logging

def connect_to_database():
    global client, db, collection
    # MongoDB 서버에 연결
    logging.info("Connecting to MongoDB...")
    client = MongoClient("mongodb://localhost:27017/")

    # 데이터베이스 선택 (예: 'mydatabase'라는 이름의 데이터베이스)
    db = client["ecoweb"]

    # 컬렉션 선택 (예: 'mycollection'이라는 이름의 컬렉션)
    collection = db["websites"]
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


def save_to_database(website_name,current_url,traffic_data,code_data):
    # 하나의 데이터에 트래픽 데이터와 코드 데이터를 합쳐서 저장
    data = {
        "website_name": website_name,
        "current_url": current_url,
        "traffic_data": traffic_data,
        "code_data": code_data
    }
    collection.insert_one(data)
    logging.info("Data saved to MongoDB")