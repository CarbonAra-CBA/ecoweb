'''
2.5만개의 공공기관 url Lighthouse 평가 결과 MongoDB에 저장 

        "institutionType": "중앙행정기관",
        "institutionCategory": "중앙행정기관",
        "institutionSubcategory": "가습기살균제사건과4.16세월호참사특별조사위원회",
        "siteName": "가습기살균제사건과4.16세월호참사특별조사위원회",
        "siteType": "웹",
        "siteLink": "http://socialdisasterscommission.go.kr/"
    },
'''
from app.services.lighthouse import run_lighthouse, process_Analysis    
import json
from utils.db_con import db_connect
from datetime import datetime

client, db, collection_traffic, collection_resource = db_connect()

# 공공기관 url 읽기 
# korea_public_website_urls.json 파일 읽기 
with open('app/data/urls/korea_public_website_urls.json', 'r', encoding='utf-8') as file:
    urls = json.load(file)

success_count = 0
error_count = 0
# 공공기관 url 각각에 대해 Lighthouse 평가 결과 MongoDB에 저장 
for url in urls:
    # http를 https 로 변경 
    url['siteLink'] = url['siteLink'].replace('http://', 'https://')
    run_lighthouse(url['siteLink'])
    signal = process_Analysis(url['siteLink'],url,collection_resource,collection_traffic)
    if signal == 1:
        print(f"현재시각: {datetime.now()}, {url['siteLink']} Done. Success!! \n Success Count: {success_count} , Error Count: {error_count}")
        success_count += 1
    else: 
        print(f"현재시각: {datetime.now()}, {url['siteLink']} URL Error. Error!! \n Success Count: {success_count} , Error Count: {error_count}")
        error_count += 1
    
print(f"Success Count: {success_count}, Error Count: {error_count}")

    

