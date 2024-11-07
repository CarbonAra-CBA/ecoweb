import os
import requests
from urllib.parse import urlparse
from ecoweb.utils.db_con import db_connect
from datetime import datetime
import logging
from ThirdPartyDetect.ThirdPartyDetect import ThirdPartyIgnore

# 로깅 설정
logging.basicConfig(filename='download_errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

def sanitize_folder_name(name):
    """디렉토리 이름에서 허용되지 않는 문자를 제거합니다."""
    return "".join(c for c in name if c.isalnum() or c in " ._-").rstrip()

def create_project_root(base_path, site_name):
    project_root = os.path.join(base_path, sanitize_folder_name(site_name))
    os.makedirs(project_root, exist_ok=True)
    return project_root

def download_resource(url, save_dir):
    """주어진 URL에서 리소스를 다운로드하여 지정된 디렉토리에 저장합니다."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)

        if not file_name:
            file_name = 'index.html' if parsed_url.path.endswith('/') else 'resource'

        file_path = os.path.join(save_dir, file_name)

        if os.path.exists(file_path):
            print(f"[{datetime.now()}] 이미 존재하는 파일: {file_path}, 스킵합니다.")
            return True

        with open(file_path, 'wb') as f:
            f.write(response.content)

        print(f"[{datetime.now()}] 다운로드 성공: {url} -> {file_path}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"다운로드 실패: {url}, 오류: {e}")
        print(f"[{datetime.now()}] 다운로드 실패: {url}, 오류: {e}")
        return False

def fetch_site_name(collection_traffic, url):
    """lighthouse_traffic 컬렉션에서 주어진 URL과 일치하는 문서의 siteName을 반환합니다."""
    normalized_url = url.replace('http://', 'https://')
    document = collection_traffic.find_one({"url": normalized_url}, {"siteName": 1, "_id": 0})

    return document.get('siteName') if document else None

def get_network_requests(collection_resource, url):
    """lighthouse_resource 컬렉션에서 주어진 URL과 일치하는 문서의 network_requests를 반환합니다."""
    normalized_url = url.replace('http://', 'https://')
    document = collection_resource.find_one({"url": normalized_url}, {"network_requests": 1, "_id": 0})

    return document.get('network_requests', []) if document else []

def download_documents(documents, root_path, base_url):
    """지정된 조건에 맞는 URL을 순회하며 파일을 다운로드하고 저장합니다."""
    urls = [doc["url"] for doc in documents if doc["resourceType"] in {"Document", "Stylesheet", "Script"}]

    for url in urls:
        relative_path = url.replace(base_url, "").lstrip("/")
        save_dir = os.path.join(root_path, os.path.dirname(relative_path))
        os.makedirs(save_dir, exist_ok=True)

        download_resource(url, save_dir)

def main():
    client, db, collection_traffic, collection_resource = db_connect()
    url = 'https://imsm.kcg.go.kr/'

    documents = get_network_requests(collection_resource=collection_resource, url=url)
    site_name = fetch_site_name(collection_traffic=collection_traffic, url=url)
    root_path = create_project_root('./', site_name)
    detectedDocs = ThirdPartyIgnore(url, documents)
    print(detectedDocs)
    download_documents(detectedDocs, root_path, url)

if __name__ == "__main__":
    main()
