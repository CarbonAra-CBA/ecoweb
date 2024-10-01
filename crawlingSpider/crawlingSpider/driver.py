from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import logging
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller

def init_driver():
    chromedriver_autoinstaller.install()

    # 크롬 옵션 설정
    options = Options()
    # options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    options.add_argument("--no-sandbox")  # no-sandbox 옵션 추가
    options.add_argument("--disable-dev-shm-usage")  # 추가
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument('--headless')  # 브라우저를 표시하지 않고 실행
    options.add_argument('--disable-web-security')  # CORS 정책 우회 설정
    options.add_argument('--ignore-certificate-errors')  # SSL 인증서 무시 설정
    options.add_argument('--log-level=3')  # 3: ERROR
    
    driver = webdriver.Chrome(options=options)
    
    return driver
    
