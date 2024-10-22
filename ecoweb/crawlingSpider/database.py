from pymongo import MongoClient
import logging

import scrapy

global client, db, website_collection , traffic_collection
    # MongoDB 서버에 연결
logging.info("Connecting to MongoDB...")
client = MongoClient("mongodb://localhost:27017/")

# 데이터베이스 선택 
db = client["ecoweb"]

# 컬렉션 리스트 
website_collection = db["websites"]
traffic_collection = db["traffic"]
logging.info("Connected to MongoDB")


def save_to_database_website(website_data):
    try: 
        website_collection.insert_one(website_data)
        logging.info(f"Saving data to database: {website_data['file_name']}")
    except Exception as e:
        logging.error(f"Error saving data to database: {e}")

def save_to_database_traffic(traffic_data):
    try:
        traffic_collection.insert_one(traffic_data)
        logging.info(f"Saving traffic data to database: {traffic_data.get('url', 'Unknown URL')}")
    except Exception as e:
        logging.error(f"Error saving traffic data to database: {str(e)}")


def find_url_in_database(url):
    # 데이터베이스에서 찾기
    code = website_collection.find_one('current_url' is url)
    traffic =traffic_collection.find_one('url' is url)

    # 있으면 return, 없으면 None 
    if code and traffic:
        return code, traffic
    else:
        return None, None