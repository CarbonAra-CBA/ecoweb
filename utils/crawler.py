import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
import chromedriver_autoinstaller

# WebDriver 초기화 함수
def initialize_driver():
    chromedriver_autoinstaller.install(True) # 강제로 최신 버전을 설치하지 않도록 설정

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-web-security')  # CORS 정책 우회 설정
    options.add_argument('--headless')

    # CORS 정책 우회 설정
    capabilities = DesiredCapabilities.CHROME.copy()
    capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}


    driver = webdriver.Chrome(options=options)
    return driver

# 데이터 크기 계산 함수 (임시로 0 반환)
def get_data_size(url):
    # URL에 따른 데이터 크기를 계산하는 실제 구현을 여기에 작성하십시오.
    return 0

# JSON 데이터 수집 함수 (주어진 URL을 크롤링하여 네트워크 요청 데이터를 수집합니다.)
def get_json_data(url):
    driver = initialize_driver()
    jsonData = []
    totSize = 0
    datasizeoftype = {"fetch": 0, "css": 0, "img": 0, "script": 0, "link": 0, "video": 0}
    content = []

    cando = ["fetch", "css", "img", "script", "link", "video"]

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        network_requests = driver.execute_script("return window.performance.getEntriesByType('resource');") # 네트워크 요청 데이터를 수집합니다.

        for entry in network_requests:
            size = get_data_size(entry["name"])
            if size is None: # 데이터 크기를 계산할 수 없는 경우(HTTP 연결 오류), 0으로 설정
                size = 0
            if entry["initiatorType"] in cando:
                print(entry["name"], entry["responseStatus"], entry["initiatorType"], size, entry["duration"], sep="\n")
                totSize += size
                datasizeoftype[entry["initiatorType"]] += size
                jsonData.append({
                    "Name": entry["name"],
                    "Status": entry["responseStatus"],
                    "Type": entry["initiatorType"],
                    "Size": size,
                    "Time": entry["duration"] # ms?
                })
        content.append({
            "URL": url,
            "Contents": jsonData,
            "Size": totSize
        })

        return content, datasizeoftype
    finally:
        driver.quit()

def get_data_size(url):
    try:
        response = requests.head(url)
        if 'content-length' in response.headers:
            content_length = int(response.headers['content-length'])
            return content_length
        else:
            print("Content length header not found.")
            return 0
    except Exception as e:
        print("Error:", e)
        return None

def preprocess_data(data):
    preprocessed_data = {}
    for website, details in data.items():
        min_co2 = float('inf')
        min_co2_details = None
        for detail_id, detail_data in details.items():
            if detail_data.get('g of CO2', float('inf')) < min_co2:
                min_co2 = detail_data['g of CO2']
                min_co2_details = detail_data
        if min_co2_details:
            preprocessed_data[website] = {min_co2_details['link']: min_co2_details}
    return preprocessed_data

