from .items import trafficItem
import json
import time
import logging
from .driver import init_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logging.basicConfig(
    level=logging.INFO,  # 로그의 기본 수준을 설정 (INFO 이상 로그가 기록됨)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 메시지의 포맷을 설정
    handlers=[
        logging.FileHandler("crawlerSecond.log", mode='w', encoding='utf-8'),  # 로그를 파일에 저장
        logging.StreamHandler()  # 콘솔에도 동시에 로그를 출력
    ]
)

class trafficSpider():
    name = 'traffic_spider'                 # 스파이더 이름 설정

    def __init__(self):
        super().__init__()
        

    def crawling_items(self, url):
        try:
            driver = init_driver()
            logging.info(f"get start: {url}")
            driver.get(url)
            logging.info(f"get end: {url}")
            WebDriverWait(driver, 10).until( # 페이지 로딩 완료 대기
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # 성능 로그 수집
            logs = driver.get_log('performance')
            resource_types = {'Document': 0, 'Stylesheet': 0, 'Script': 0, 'Image': 0, 'Media': 0, 'Other': 0}
            total_size = 0
            logging.info(f"start traffic log")
            for log in logs:
                # logging.info(f"log >>>: {log}")                                         # 전체 프로세스 출력
                message = json.loads(log["message"])["message"]
                if "Network.responseReceived" == message["method"]:
                    mime_type = message['params']['response']['mimeType']
                    resource_size = message['params']['response']['encodedDataLength']

                    # 상태 코드 확인 (200 OK인 경우만 처리)
                    if message['params']['response']['status'] != 200:
                        continue
                    resource_types, total_size = update_resource_types(resource_types, mime_type, resource_size, message['params']['response']['url'])
                # time.sleep(0.1) 불필요함

            if not logs:
                logging.warning(f"No performance logs collected for URL: {url}")
                return {'url': url, 'css': 0, 'image': 0, 'media': 0, 'script': 0, 'total_size': 0}
            
            traffic_resource = create_traffic_item(url, resource_types, total_size)
            return dict(traffic_resource)
        except Exception as e:
            logging.error(f"Error in crawling_items for {url}: {str(e)}")
            return None
        finally:
            # 드라이버 종료
            driver.quit()


def update_resource_types(resource_types, mime_type, resource_size, url):
    if 'text/html' in mime_type:
        resource_types['Document'] += resource_size
    elif 'text/css' in mime_type:
        resource_types['Stylesheet'] += resource_size
    elif 'application/javascript' in mime_type or 'application/x-javascript' in mime_type or 'text/javascript' in mime_type:
        resource_types['Script'] += resource_size
    elif 'image' in mime_type or ('application/octet-stream' in mime_type and any(ext in url for ext in ['.png', '.jpg', '.jpeg', '.gif'])):
        resource_types['Image'] += resource_size
    elif 'video' in mime_type or 'audio' in mime_type:
        resource_types['Media'] += resource_size
    else:
        resource_types['Other'] += resource_size
    return resource_types, resource_size

def create_traffic_item(url, resource_types, total_size):
    
    traffic_resource = trafficItem()
    traffic_resource['url'] = url
    traffic_resource['document'] = resource_types['Document']
    traffic_resource['css'] = resource_types['Stylesheet']
    traffic_resource['image'] = resource_types['Image']
    traffic_resource['media'] = resource_types['Media']
    traffic_resource['script'] = resource_types['Script']
    traffic_resource['total_size'] = traffic_resource['css'] + traffic_resource['image'] + traffic_resource['media'] + traffic_resource['script']
    return traffic_resource
