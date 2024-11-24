import json
import subprocess
import os

def run_lighthouse(url):
    # 아래는 리눅스 환경에서 동작하지 않아서 폐기예정(정확도가 떨어지지만 어쩔 수 없다. -> 근데 스크린샷 문제는 아직 해결 못함. (터미널에서 어떻게 스크린샷을 찍음..))
    # command = f'lighthouse {url} --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'
    command = f'lighthouse {url} --chrome-flags="--headless --no-sandbox --disable-gpu --disable-dev-shm-usage" --only-audits=network-requests,resource-summary,third-party-summary,script-treemap-data,total-byte-weight,unused-css-rules,,unused-javascript,modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries --output json --output-path ./report.json --preset=desktop'

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
    
# def run_lighthouse(url):
#     try:
#         # Chrome 플래그 설정
#         chrome_flags = [
#             '--headless',
#             '--no-sandbox',
#             '--disable-gpu',
#             '--disable-dev-shm-usage',
#             '--disable-software-rasterizer',
#             '--disable-setuid-sandbox',
#             '--no-zygote',
#             '--single-process',
#             '--remote-debugging-port=9222'
#         ]
        
#         # Lighthouse 명령어 구성
#         command = [
#             'lighthouse',
#             url,
#             f'--chrome-flags="{" ".join(chrome_flags)}"',
#             '--only-audits=network-requests,resource-summary,third-party-summary,'
#             'script-treemap-data,total-byte-weight,unused-css-rules,unused-javascript,'
#             'modern-image-formats,efficient-animated-content,duplicated-javascript,js-libraries',
#             '--output=json',
#             '--output-path=./report.json',
#             '--preset=desktop',
#             '--verbose'  # 디버깅을 위한 상세 로그
#         ]
        
#         # 명령어를 문자열로 결합
#         command_str = ' '.join(command)
        
#         # 실행 전 디버그 정보 출력
#         print(f"Executing Lighthouse command: {command_str}")
        
#         # Lighthouse 실행
#         process = subprocess.run(
#             command_str,
#             shell=True,
#             capture_output=True,
#             text=True
#         )
        
#         # 실행 결과 확인
#         if process.returncode != 0:
#             print("Lighthouse execution failed:")
#             print(f"Error output: {process.stderr}")
#             print(f"Standard output: {process.stdout}")
#             raise Exception(f"Lighthouse failed with return code {process.returncode}")
            
#         # 결과 파일 확인
#         if not os.path.exists('./report.json'):
#             raise FileNotFoundError("Lighthouse report file was not created")
            
#         # 결과 파일 크기 확인
#         if os.path.getsize('./report.json') == 0:
#             raise Exception("Lighthouse report file is empty")
            
#         print("Lighthouse execution completed successfully")
#         return True
        
#     except Exception as e:
#         print(f"Error running Lighthouse: {str(e)}")
#         return False

def process_report(url, collection_resource, collection_traffic):
    try:
        with open('report.json', 'r', encoding='utf-8') as file:
            report = json.load(file)

        # 1. 기본 데이터 구조 검증
        if 'audits' not in report:
            raise KeyError("Report doesn't contain 'audits' section")

        # 2. network-requests 검증
        network_requests = report.get('audits', {}).get('network-requests', {}).get('details', {}).get('items', [])
        if not network_requests:
            print(f"Warning: No network requests found for {url}")

        # 3. resource-summary 검증
        resource_summary = report.get('audits', {}).get('resource-summary', {}).get('details', {}).get('items', [])
        if not resource_summary:
            raise KeyError("No resource summary data found")

        # MongoDB에 저장할 데이터 추출
        # 만약, details가 없는 경우, 빈 리스트를 사용(get 메서드 사용)
         # 4. 리소스 데이터 추출 with 상세한 예외 처리
        try:
            total_resource_bytes = resource_summary[0].get('transferSize', 0)
            resource_bytes = {
                'font_total_bytes': resource_summary[1].get('transferSize', 0) if len(resource_summary) > 1 else 0,
                'script_total_bytes': resource_summary[2].get('transferSize', 0) if len(resource_summary) > 2 else 0,
                'html_total_bytes': resource_summary[3].get('transferSize', 0) if len(resource_summary) > 3 else 0,
                'css_total_bytes': resource_summary[4].get('transferSize', 0) if len(resource_summary) > 4 else 0,
                'other_total_bytes': resource_summary[5].get('transferSize', 0) if len(resource_summary) > 5 else 0,
                'media_total_bytes': resource_summary[6].get('transferSize', 0) if len(resource_summary) > 6 else 0,
                'third_party_total_bytes': resource_summary[7].get('transferSize', 0) if len(resource_summary) > 7 else 0
            }
        except IndexError as e:
            print(f"Warning: Incomplete resource summary for {url}: {str(e)}")
            resource_bytes = {k: 0 for k in ['font_total_bytes', 'script_total_bytes', 'html_total_bytes', 
                                           'css_total_bytes', 'other_total_bytes', 'media_total_bytes', 
                                           'third_party_total_bytes']}

        # 5. MongoDB 데이터 준비 with 검증
        traffic_data = {
            'url': url,
            'resource_summary': []
        }

        for item in resource_summary:
            if not isinstance(item, dict):
                print(f"Warning: Invalid resource summary item format for {url}")
                continue
            traffic_data['resource_summary'].append({
                'resourceType': item.get('resourceType', 'unknown'),
                'transferSize': item.get('transferSize', 0)
            })

        resource_data = {
            'url': url,
            'network_requests': []
        }

        for item in network_requests:
            if not isinstance(item, dict):
                print(f"Warning: Invalid network request item format for {url}")
                continue
            if item.get('resourceSize', 0) != 0 or item.get('mimeType', '') != '':
                resource_data['network_requests'].append({
                    'url': item.get('url', ''),
                    'resourceType': item.get('resourceType', 'unknown'),
                    'resourceSize': item.get('resourceSize', 0)
                })

        # 6. MongoDB 저장 with 예외 처리
        try:
            collection_traffic.insert_one(traffic_data)
            collection_resource.insert_one(resource_data)
        except Exception as e:
            print(f"MongoDB insertion error for {url}: {str(e)}")
    
        # 7. 스크립트 데이터 처리
        script_treemap_data = safe_get_audit_value(report, ['script-treemap-data', 'details', 'nodes'], [])
        
        # 8. view_data 준비
        view_data = {
            'third_party_summary_wasted_bytes': safe_get_audit_value(
                report, ['third-party-summary', 'details', 'summary', 'wastedBytes']
            ),
            'total_unused_bytes_script': sum(node.get('unusedBytes', 0) for node in script_treemap_data),
            'total_resource_bytes_script': sum(node.get('resourceBytes', 0) for node in script_treemap_data),
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
            **resource_bytes  # 위에서 준비한 resource_bytes 딕셔너리를 풀어서 넣기
        }

        return view_data

    except Exception as e:
        print(f"Detailed error in process_report for {url}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Stack trace:\n{traceback.format_exc()}")
        
        # 기본 view_data 반환
        return {
            'total_byte_weight': 0,
            'third_party_summary_wasted_bytes': 0,
            'total_unused_bytes_script': 0,
            'total_resource_bytes_script': 0,
            'can_optimize_css_bytes': 0,
            'can_optimize_js_bytes': 0,
            'modern_image_formats_bytes': 0,
            'efficient_animated_content': 0,
            'duplicated_javascript': 0,
            'font_total_bytes': 0,
            'script_total_bytes': 0,
            'html_total_bytes': 0,
            'css_total_bytes': 0,
            'other_total_bytes': 0,
            'media_total_bytes': 0,
            'third_party_total_bytes': 0
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