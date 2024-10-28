import json
import subprocess
from utils.db_con import db_connect

def run_lighthouse(url):
    command = f'lighthouse {url} --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'
    subprocess.run(command, shell=True)



def process_report(url,collection_resource,collection_traffic):
    with open('report.json', 'r') as file:
        report = json.load(file)
    
    # MongoDB에 저장할 데이터 추출
    network_requests = report['audits']['network-requests']['details']['items']
    resource_summary = report['audits']['resource-summary']['details']['items']

    traffic_data = {
        'url' : url,
        'resource_summary' : [{'resourceType': item['resourceType'], 'transferSize': item['transferSize']} for item in resource_summary],
    }

    resource_data = {
        'url' : url,
        'network_requests': [{'url': item['url'], 'resourceType': item['resourceType']} for item in network_requests],
    }

    # MongoDB에 저장
    collection_traffic.insert_one(traffic_data)
    collection_resource.insert_one(resource_data)
    
    # 뷰에 전달할 데이터 준비 (python flask 에서 view로 전달. .. )
    view_data = {
        'third_party_summary': report['audits']['third-party-summary'],
        'script_treemap_data': report['audits']['script-treemap-data'],
        'total_byte_weight': report['audits']['total-byte-weight']['numericValue'],
        'unused_css_rules': report['audits']['unused-css-rules'],
        'unused_javascript': report['audits']['unused-javascript'],
        'modern_image_formats': report['audits']['modern-image-formats'],
        'efficient_animated_content': report['audits']['efficient-animated-content'],
        'duplicated_javascript': report['audits']['duplicated-javascript'],
        'js_libraries': report['audits']['js-libraries']
    }

    return view_data