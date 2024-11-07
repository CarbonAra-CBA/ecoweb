import json
import subprocess

def run_lighthouse(url):
    command = f'lighthouse {url} --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'
    subprocess.run(command, shell=True)


def process_report(url,collection_resource,collection_traffic):
    with open('report.json', 'r', encoding='utf-8') as file:
        report = json.load(file)
    
    # MongoDB에 저장할 데이터 추출
    network_requests = report['audits']['network-requests']['details']['items']
    resource_summary = report['audits']['resource-summary']['details']['items']
    try:
        traffic_data = {
            'url' : url,
            'resource_summary' : [{'resourceType': item['resourceType'], 'transferSize': item['transferSize']} for item in resource_summary],
        }

        resource_data = {
            'url' : url,
            'network_requests': [{'url': item['url'], 'resourceType': item['resourceType'], 'resourceSize': item['resourceSize']} for item in network_requests],
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
    except:
        print(f"Error in process_report: {url}")
        
    return view_data

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
        print('traffic_data')
        print(traffic_data)
        print('resource_data')
        print(resource_data)
        # MongoDB에 저장
        collection_traffic.insert_one(traffic_data)
        # collection_traffic.insert_one(url_data)
        collection_resource.insert_one(resource_data)
    except Exception as e:
        print(f"Error in process_Analysis: {url}, {e}")
        return 0
    return 1