import json
import json
import subprocess
import os
from pymongo import MongoClient
from bson.json_util import dumps

client = MongoClient('mongodb://localhost:27017/')
db = client['ecoweb']
collection_traffic = db['lighthouse_traffic']
collection_resource = db['lighthouse_resource']

def run_lighthouse(url):
    command = f'lighthouse {url} --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'
    subprocess.run(command, shell=True)

def process_report(url):
    with open('report.json', 'r') as file:
        report = json.load(file)
    
    # MongoDB에 저장할 데이터 추출
    network_requests = report['audits']['network-requests']['details']['items']
    resource_summary = report['audits']['resource-summary']['details']['items']

    traffic_data = {
        'url' : url,
        'network_requests': [{'url': item['url'], 'type': item['resourceType']} for item in network_requests],
    }

    resource_data = {
        'url' : url,
        'resource_summary' : [{'type': item['resourceType'], 'transferSize': item['transferSize']} for item in resource_summary],
    }

    # MongoDB에 저장
    collection_traffic.insert_one(traffic_data)
    collection_resource.insert_one(resource_data)

    # # 뷰에 전달할 데이터 준비 (python flask 에서 view로 전달. .. )
    # view_data = {
    #     'third_party_summary': report['audits']['third-party-summary'],
    #     'script_treemap_data': report['audits']['script-treemap-data'],
    #     'total_byte_weight': report['audits']['total-byte-weight'],
    #     'unused_css_rules': report['audits']['unused-css-rules'],
    #     'unused_javascript': report['audits']['unused-javascript'],
    #     'modern_image_formats': report['audits']['modern-image-formats'],
    #     'efficient_animated_content': report['audits']['efficient-animated-content'],
    #     'duplicated_javascript': report['audits']['duplicated-javascript'],
    #     'js_libraries': report['audits']['js-libraries']
    # }

    # return view_data

def get_report_imagepath():  # 라이트하우스가 이미 실행되어 report.json 이 존재한다고 했을때, 이미지 파일들의 path를 리턴
    json_file = open('../ecoweb/report.json', 'r')
    report = json.load(json_file)
    image_url_list = []
    for item in report['audits']['network-requests']['details']['items']:
        file_url = item['url']
        file_url_split = re.split(r':|\/|\.', file_url)
        if file_url_split[-1] == 'jpg' or file_url_split[-1] == 'jpeg' or file_url_split[-1] == 'png':
            image_url_list.append(file_url)

    return image_url_list

def main():
    json_path = "../urls/env_urls.json"
    with open(json_path, 'r') as json_file:
        json_data = json.load(json_file)
    
    for item in json_data:
        url = item["사이트링크"]
        print(f"Processing: {url}")
        
        run_lighthouse(url)
        view_data = process_report(url)
        
        # # 뷰에 데이터 전달 (예: JSON 파일로 저장)
        # with open(f'view_data_{url.replace("://", "_").replace("/", "_")}.json', 'w') as f:
        #     json.dump(view_data, f, ensure_ascii=False, indent=2)
        
        print(f"Completed: {url}")

if __name__ == "__main__":
    main()