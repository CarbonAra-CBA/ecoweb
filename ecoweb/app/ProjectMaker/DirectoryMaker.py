import os
import requests
from urllib.parse import urlparse
from datetime import datetime
import logging
import json

logging.basicConfig(filename='download_errors.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

def is_node_module(url):
    """URL이 node_modules 관련인지 확인"""
    node_patterns = [
        'node_modules',
        'npm',
        'unpkg.com',
        'cdnjs',
        'jsdelivr',
        'webpack',
    ]
    return any(pattern in url.lower() for pattern in node_patterns)

def sanitize_folder_name(name):
    """디렉토리 이름에서 허용되지 않는 문자를 제거합니다."""
    return "".join(c for c in name if c.isalnum() or c in " ._-").rstrip()

def create_project_root(base_path, site_name):
    sanitized_site_name = sanitize_folder_name(site_name)
    project_root = os.path.join(base_path, sanitized_site_name)
    os.makedirs(project_root, exist_ok=True)
    return project_root

def download_resource(url, save_dir):
    """node_modules 관련 리소스는 제외하고 다운로드"""
    if is_node_module(url):
        print(f"[{datetime.now()}] Node module 리소스 스킵: {url}")
        return False
        
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
    """node_modules 관련 요청 제외"""
    normalized_url = url.replace('http://', 'https://')
    document = collection_resource.find_one({"url": normalized_url}, {"network_requests": 1, "_id": 0})
    
    if document and 'network_requests' in document:
        # node_modules 관련 요청 필터링
        filtered_requests = [
            req for req in document['network_requests']
            if not is_node_module(req.get('url', ''))
        ]
        return filtered_requests
    return []

def download_documents(documents, root_path, base_url):
    """필터링된 URL만 다운로드"""
    urls = [doc["url"] for doc in documents if not is_node_module(doc["url"])]

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
    root_path = create_project_root('./ecoweb/app/static/webprojects', site_name)
    
    # node_modules 관련 요청이 제외된 문서 가져오기
    documents = get_network_requests(collection_resource=collection_resource, url=url)
    
    print("Filtered documents count:", len(documents))
    print("root_path:", root_path)
    
    download_documents(documents, root_path, parsed_url)
    return root_path

def get_directory_structure(root_dir):
    """
    Recursively builds a JSON-like dictionary that represents
    the file and directory structure under the given root directory.
    """
    structure = {}

    # Iterate over each item in the root directory
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path):  # If it's a directory
            # Recurse into the directory
            structure[item] = get_directory_structure(item_path)
        elif os.path.isfile(item_path):  # If it's a file
            # Add the file name to the list
            structure.setdefault("__files__", []).append(item)

    return structure

def directory_to_json(root_path):
    """
    Converts the directory structure into JSON format and optionally saves it to a file.
    """
    if not os.path.isdir(root_path):
        raise ValueError(f"Provided path '{root_path}' is not a valid directory.")

    # Build the directory structure as a nested dictionary
    dir_structure = get_directory_structure(root_path)

    # Convert the dictionary to JSON
    json_data = json.dumps(dir_structure, indent=4)
    json_data = json.loads(json_data)

    return json_data

if __name__ == "__main__":
    url = "https://me.go.kr/"
    # client, db, collection_traffic, collection_resource = db_connect()
    # directory_maker(url, collection_traffic, collection_resource)
    # root_path = "./ecoweb/ecoweb/app/static/webprojects/me.go.kr/"
    root_path = "./ecoweb/app/static/webprojects/me.go.kr"
    json_data = directory_to_json(root_path)
    # JSON 파일로 저장
    output_path = os.path.join(os.path.dirname(root_path), 'directory_structure.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    print(f"Directory structure has been saved to: {output_path}")