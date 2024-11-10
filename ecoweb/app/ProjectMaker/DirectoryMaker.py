import os
import requests
from urllib.parse import urlparse
from datetime import datetime
import logging
from ecoweb.app.ProjectMaker.ThirdPartyDetect import ThirdPartyIgnore

# 로깅 설정
logging.basicConfig(filename='download_errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')


def sanitize_folder_name(name):
    """디렉토리 이름에서 허용되지 않는 문자를 제거합니다."""
    return "".join(c for c in name if c.isalnum() or c in " ._-").rstrip()


def create_project_root(base_path, site_name):
    sanitized_site_name = sanitize_folder_name(site_name)
    project_root = os.path.join(base_path, sanitized_site_name)
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

        # 파일 경로 생성 시 ':' 및 '?' 같은 허용되지 않는 문자를 '_'로 대체
        sanitized_file_name = file_name.replace(':', '_').replace('?', '_')
        file_path = os.path.join(save_dir, sanitized_file_name)

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

def get_network_requests(collection_resource, url):
    """lighthouse_resource 컬렉션에서 주어진 URL과 일치하는 문서의 network_requests를 반환합니다."""
    normalized_url = url.replace('http://', 'https://')
    document = collection_resource.find_one({"url": normalized_url}, {"network_requests": 1, "_id": 0})

    return document.get('network_requests', []) if document else []


def download_documents(documents, root_path, base_url):
    """지정된 조건에 맞는 URL을 순회하며 파일을 다운로드하고 저장합니다."""
    urls = [doc["url"] for doc in documents if doc["resourceType"] in {"Document", "Stylesheet", "Script"}]

    for url in urls:
        parsed_url = urlparse(url)

        # 도메인을 삭제하고 나머지 경로를 로컬 경로로 변환
        # URL 경로에서 시작 슬래시를 제거하고, '/'를 로컬 경로 구분자로 대체
        directory_path = parsed_url.path.lstrip('/').replace('/', os.sep)

        # 로컬 저장 경로 생성
        save_dir = os.path.join(root_path, os.path.dirname(directory_path))
        os.makedirs(save_dir, exist_ok=True)

        # 파일 이름 지정 (쿼리 스트링 제거)
        file_name = os.path.basename(parsed_url.path.split('?')[0])

        # 최종 파일 경로 생성
        file_path = os.path.join(save_dir, file_name)

        # 파일 다운로드 및 저장
        download_resource(url, save_dir)



def directory_maker(url, collection_traffic, collection_resource):
    # 사이트 이름을 URL의 도메인 부분으로 설정
    parsed_url = urlparse(url)
    site_name = parsed_url.netloc

    # 프로젝트 루트 경로 생성
    root_path = create_project_root('C:/Users/windowadmin1.WIN-TAQQ3RO5V1L.000/Desktop/ecoweb/ecoweb/llama/', site_name)

    # 네트워크 요청과 감지 문서 가져오기
    documents = get_network_requests(collection_resource=collection_resource, url=url)
    detectedDocs = ThirdPartyIgnore(url_list=documents)

    print(detectedDocs)
    print("root_path : ", root_path)
    download_documents(detectedDocs, root_path, url)
    return root_path


if __name__ == "__main__":
    url = "https://me.go.kr/"
    client, db, collection_traffic, collection_resource = db_connect()
    directory_maker(url, collection_traffic, collection_resource)