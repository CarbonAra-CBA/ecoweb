import subprocess
import json
import os
import re

def run_lighthouse(chromePath, url, outputPath):
    # Lighthouse CLI 명령어 실행 (절대 경로 사용)
    result = subprocess.run(
        ['lighthouse', url, '--output=json', f'--output-path={outputPath}', '--chrome-path', chromePath],
        capture_output=True,
        text=True,
        encoding='utf-8',  # UTF-8 인코딩 사용
        shell=True  # Windows에서는 shell=True 필요
    )

    # 결과 확인
    if result.returncode != 0:
        print("Error running Lighthouse:", result.stderr)
        return None

    # JSON 보고서 파일 읽기
    with open(outputPath, 'r', encoding='utf-8') as f:  # UTF-8 인코딩 사용
        report_json = json.load(f)

    return report_json


def is_valid_path(path):
    # 경로가 존재하고, 파일인지 확인
    return os.path.isfile(path)

def is_valid_url(url):
    # URL 유효성 검사 (정규 표현식 사용)
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// 또는 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # 도메인...
        r'localhost|'  # 또는 localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # 또는 IP 주소...
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # 또는 IPv6 주소...
        r'(?::\d+)?'  # 선택적 포트 번호...
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# 입력 받기
while True:
    chromePath = input("Enter chrome path (absolute): ")
    # 유효한 절대 경로가 아니면 다시 입력 받기
    if is_valid_path(chromePath) and chromePath.endswith('chrome.exe'):
        break
    else:
        print("Invalid chrome path. Please enter a valid absolute path to the Chrome executable.")

while True:
    url = input("Enter URL (for report): ")
    # 유효한 url이 아니면 다시 입력 받기
    if is_valid_url(url):
        break
    else:
        print("Invalid URL. Please enter a valid URL.")

# 출력 경로 입력 받기
while True:
    outputPath = input("Enter the relative path for the report (e.g., ./report.json): ")
    # 유효한 절대 경로가 아니면 다시 입력 받기
    if is_valid_path(outputPath) and outputPath.endswith('report.json'):
        break
    else:
        print("Invalid output path. Please enter a valid output path(e.g., ./report.json)")

# Lighthouse 실행 및 보고서 저장
report = run_lighthouse(chromePath, url, outputPath)

# 결과 출력 (예: 보고서의 일부를 출력)
if report:
    print(json.dumps(report, indent=2))

# 보고서를 JSON 객체로 저장
report_json_object = report

# json 객체로 저장된 보고서를 데이터베이스에 전송(작성 필요)