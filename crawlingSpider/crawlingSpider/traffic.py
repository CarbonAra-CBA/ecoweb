from scrapy.spiders import CrawlSpider
from items import trafficItem
from driver import Driver
import json
import time
'''
issue:
1. driver session(생성되고 종료되기까지의 간격 사이에 sleep() 을 주지 않으면 session it not created 에러 발생)

'''
class trafficSpider(CrawlSpider):
    name = 'traffic_spider'  # 스파이더 이름 설정
    allowed_domains = ['naver.com']  # 허용할 도메인 설정
    start_urls = ['https://www.naver.com']  # 시작할 URL 설정

    @staticmethod
    def crawling_items(url):
        driver = Driver().init_driver()
        driver.get(url)
        resource_types = {'Document': 0, 'Stylesheet': 0, 'Script': 0, 'Image': 0, 'Media': 0, 'Other': 0}
        total_size = 0

        for log in driver.get_log('performance'):
            message = json.loads(log["message"])["message"]
            if "Network.responseReceived" == message["method"]:
                mime_type = message['params']['response']['mimeType']
                resource_size = message['params']['response']['encodedDataLength']
                resource_types, total_size = update_resource_types(resource_types, mime_type, resource_size, message['params']['response']['url'])
                time.sleep(0.1)

        driver.quit()
        traffic_resource = create_traffic_item(url, resource_types, total_size)
        return traffic_resource

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
    traffic_resource['total_size'] = total_size
    return traffic_resource
