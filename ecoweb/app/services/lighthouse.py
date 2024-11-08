import json
import subprocess
from utils.db_con import db_connect

def run_lighthouse(url):
    command = f'lighthouse {url} --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'
    subprocess.run(command, shell=True)

def process_report(url, collection_resource, collection_traffic):
    try:
        with open('report.json', 'r', encoding='utf-8') as file:
            report = json.load(file)
        
        # MongoDB에 저장할 데이터 추출
        network_requests = report['audits']['network-requests']['details']['items']
        resource_summary = report['audits']['resource-summary']['details']['items']
        
        traffic_data = {
            'url': url,
            'resource_summary': [{'resourceType': item['resourceType'], 'transferSize': item['transferSize']} for item in resource_summary],
        }

        resource_data = {
            'url': url,
            'network_requests': [{'url': item['url'], 'resourceType': item['resourceType'], 'resourceSize': item['resourceSize']} for item in network_requests],
        }

        # MongoDB에 저장
        collection_traffic.insert_one(traffic_data)
        collection_resource.insert_one(resource_data)
        
        # unusedBytes, resourceBytes 합산
        script_treemap_data = report['audits']['script-treemap-data']['details']['nodes']
        total_unused_bytes = 0
        total_resource_bytes = 0
        for node in script_treemap_data:
            total_unused_bytes += node['unusedBytes']
            total_resource_bytes += node['resourceBytes']
        
        third_party_summary_wasted_bytes = report['audits']['third-party-summary']['details']['summary']['wastedBytes']
        modern_image_formats = report['audits']['modern-image-formats']['details']['overallSavingsBytes']

    
        # 뷰에 전달할 데이터 준비
        view_data = {
            'third_party_summary_wasted_bytes': third_party_summary_wasted_bytes,
            'total_unused_bytes': total_unused_bytes,
            'total_resource_bytes': total_resource_bytes,
            'total_byte_weight': report['audits']['total-byte-weight']['numericValue'],
            'can_optimize_css_bytes': report['audits']['unused-css-rules']['details']['overallSavingsBytes'], # 최적화 가능한 css 용량
            'can_optimize_js_bytes': report['audits']['unused-javascript']['details']['overallSavingsBytes'], # 최적화 가능한 js 용량
            'modern_image_formats_bytes': modern_image_formats, # webp로 변환 시 절약되는 용량
            'efficient_animated_content': report['audits']['efficient-animated-content']['details']['overallSavingsBytes'], # 최적화 가능한 애니메이션 용량
            'duplicated_javascript': report['audits']['duplicated-javascript']['numericValue'], # 중복된 js 모듈 용량
            # 'js_libraries': report['audits']['js-libraries']
        }

        print("view_data['total_byte_weight'] on lighthouse.py: ", view_data['total_byte_weight'])
        print("\n")
        print("view_data on lighthouse.py: ", view_data)
        return view_data
        
    except Exception as e:
        print(f"Error in process_report: {url}, {str(e)}")
        # 기본 view_data 반환
        return {
            'total_byte_weight': 0,
            'third_party_summary': {},
            'script_treemap_data': {},
            'unused_css_rules': {},
            'unused_javascript': {},
            'modern_image_formats': {},
            'efficient_animated_content': {},
            'duplicated_javascript': {},
            'js_libraries': {}
        }

# 공공기관 url 각각에 대해 Lighthouse 평가 결과 MongoDB에 저장 
def process_Analysis(url,url_data,collection_resource,collection_traffic):
    with open('report.json', 'r', encoding='utf-8') as file:
        report = json.load(file)
    try:
        # MongoDB에 저장할 데이터 추출
        network_requests = report['audits']['network-requests']['details']['items']
        resource_summary = report['audits']['resource-summary']['details']['items']
        
        # resourceType 이 없는 경우는 'unknown'으로 저장하고 transferSize 가 없는 경우는 0으로 저장한다.
        traffic_data = {
            'url' : url,
            'resource_summary' : [
                {'resourceType': item.get('resourceType', 'unknown'), 'transferSize': item.get('transferSize', 0)} 
                for item in resource_summary
            ],
            # url_data에 있는 요소 전부 넣기
            **url_data
        }

        resource_data = {
            'url': url,
            'network_requests': [
                {
                    'url': item.get('url', ''),
                    'resourceType': item.get('resourceType', 'unknown'),
                    'resourceSize': item.get('resourceSize', 0)
                } for item in network_requests
            ],
        }

        # MongoDB에 저장
        collection_traffic.insert_one(traffic_data)
        # collection_traffic.insert_one(url_data)
        collection_resource.insert_one(resource_data)
    except Exception as e:
        print(f"Error in process_Analysis: {url}, {e}")
        return 0
    return 1