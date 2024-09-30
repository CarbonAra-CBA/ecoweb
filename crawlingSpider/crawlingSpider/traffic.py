from scrapy.spiders import CrawlSpider
from items import trafficItem
import json
import time
import logging
from driver import Driver

logging.basicConfig(
    level=logging.INFO,  # 로그의 기본 수준을 설정 (INFO 이상 로그가 기록됨)
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 메시지의 포맷을 설정
    handlers=[
        logging.FileHandler("crawlerSecond.log", mode='w', encoding='utf-8'),  # 로그를 파일에 저장
        logging.StreamHandler()  # 콘솔에도 동시에 로그를 출력
    ]
)

class trafficSpider(CrawlSpider):
    name = 'traffic_spider'                 # 스파이더 이름 설정
    

    def __init__(self):
        self.driver = Driver().init_driver()  # 드라이버 초기화

    @staticmethod
    def crawling_items(self, url):
        logging.info(f"start traffic data crawling at {url}")
        self.driver.get_url(url)
        resource_types = {'Document': 0, 'Stylesheet': 0, 'Script': 0, 'Image': 0, 'Media': 0, 'Other': 0}
        total_size = 0

        for log in self.driver.get_log('performance'):
            message = json.loads(log["message"])["message"]
            if "Network.responseReceived" == message["method"]:
                mime_type = message['params']['response']['mimeType']
                resource_size = message['params']['response']['encodedDataLength']
                resource_types, total_size = update_resource_types(resource_types, mime_type, resource_size, message['params']['response']['url'])
                time.sleep(0.1)

        traffic_resource = create_traffic_item(url, resource_types, total_size)
        
        # 드라이버 종료
        self.driver.close_driver()

        return dict(traffic_resource)


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
    traffic_resource['css'] = resource_types['Stylesheet']
    traffic_resource['image'] = resource_types['Image']
    traffic_resource['media'] = resource_types['Media']
    traffic_resource['script'] = resource_types['Script']
    traffic_resource['total_size'] = traffic_resource['css'] + traffic_resource['image'] + traffic_resource['media'] + traffic_resource['script']
    return traffic_resource
