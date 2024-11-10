import json
import subprocess

def run_lighthouse(url):
    command = f'lighthouse {url} --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'
    subprocess.run(command, shell=True)

def safe_get_audit_value(report, audit_path, default_value=0):
    """안전하게 audit 값을 가져오는 헬퍼 함수"""
    try:
        result = report['audits']
        for key in audit_path:
            result = result[key]
        return result
    except (KeyError, TypeError):
        return default_value


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
            'network_requests': [],
        }
        # resourcetype이 없는 경우(mimeType이 '' 인 경우) resourceSize도 0인 경우, resource_data에 넣지 않아야함. 
        for item in network_requests:
            if item['resourceSize'] != 0 or item['mimeType'] != '':
                resource_data['network_requests'].append({'url': item['url'], 'resourceType': item['resourceType'], 'resourceSize': item['resourceSize']})
        print('traffic_data on lighthouse.py: ', traffic_data)
        print("resource_data on lighthouse.py: ", resource_data)
        # MongoDB에 저장
        collection_traffic.insert_one(traffic_data)
        collection_resource.insert_one(resource_data)
        
        # unusedBytes, resourceBytes 합산
        # script_treemap_data = safe_get_audit_value(report, ['script-treemap-data', 'details', 'nodes'], [])
        # total_unused_bytes = 0
        # total_resource_bytes = 0
        # for node in script_treemap_data:
        #     total_unused_bytes += node['unusedBytes']
        #     total_resource_bytes += node['resourceBytes']
        script_treemap_data = safe_get_audit_value(report, ['script-treemap-data', 'details', 'nodes'], [])
        total_unused_bytes = sum(node.get('unusedBytes', 0) for node in script_treemap_data)
        total_resource_bytes = sum(node.get('resourceBytes', 0) for node in script_treemap_data)
        
        # 뷰에 전달할 데이터 준비
        view_data = {
            'third_party_summary_wasted_bytes': safe_get_audit_value(
                report, ['third-party-summary', 'details', 'summary', 'wastedBytes']
            ),
            'total_unused_bytes': total_unused_bytes,
            'total_resource_bytes': total_resource_bytes,
            'total_byte_weight': safe_get_audit_value(
                report, ['total-byte-weight', 'numericValue']
            ),
            'can_optimize_css_bytes': safe_get_audit_value(
                report, ['unused-css-rules', 'details', 'overallSavingsBytes']
            ),
            'can_optimize_js_bytes': safe_get_audit_value(
                report, ['unused-javascript', 'details', 'overallSavingsBytes']
            ),
            'modern_image_formats_bytes': safe_get_audit_value(
                report, ['modern-image-formats', 'details', 'overallSavingsBytes']
            ),
            'efficient_animated_content': safe_get_audit_value(
                report, ['efficient-animated-content', 'details', 'overallSavingsBytes']
            ),
            'duplicated_javascript': safe_get_audit_value(
                report, ['duplicated-javascript', 'numericValue']
            ),
        }

        return view_data
    
    # 좀 더 세밀한 예외처리 필요
    except Exception as e:
        print(f"Error in process_report: {url}, {str(e)}")
        print("view_data on lighthouse.py: ", view_data)
        # 기본 view_data 반환
        return {
            'total_byte_weight': 0,
            'third_party_summary_wasted_bytes': 0,
            'total_unused_bytes': 0,
            'total_resource_bytes': 0,
            'can_optimize_css_bytes': 0,
            'can_optimize_js_bytes': 0,
            'modern_image_formats_bytes': 0,
            'efficient_animated_content': 0,
            'duplicated_javascript': 0
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