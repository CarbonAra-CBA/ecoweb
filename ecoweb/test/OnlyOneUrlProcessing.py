from app.services.lighthouse import run_lighthouse, process_Analysis
import json
from utils.db_con import db_connect
from datetime import datetime

client, db, collection_traffic, collection_resource = db_connect()

if __name__ == "__main__":

    url = {
        "institutionType": "중앙행정기관",
        "institutionCategory": "해양경찰청",
        "institutionSubcategory": "해양경찰청",
        "siteName": "수상안전 종합정보",
        "siteType": "웹",
        "siteLink": "https://imsm.kcg.go.kr/"
    }
    url['siteLink'] = url['siteLink'].replace('http://', 'https://')
    run_lighthouse(url['siteLink'])
    signal = process_Analysis(url['siteLink'], url, collection_resource, collection_traffic)
    if signal == 1:
        print(
            f"현재시각: {datetime.now()}, {url['siteLink']} Done. Success!!")
    else:
        print(
            f"현재시각: {datetime.now()}, {url['siteLink']} URL Error. Error!!")
