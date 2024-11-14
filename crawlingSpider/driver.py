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
    options.add_argument('--enable-cookies') # 쿠키 허용 
    options.add_argument("--disable-dev-shm-usage")  # 추가
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    options.add_argument('--headless=new')  # 브라우저를 표시하지 않고 실행
    options.add_argument('--disable-web-security')  # CORS 정책 우회 설정
    options.add_argument('--ignore-certificate-errors')  # SSL 인증서 무시 설정
    options.add_argument('--log-level=3')  # 3: ERROR
    # options.add_argument('--enable-javascript') # 자바스크립트 동적 웹 페이지 렌더링 가능, 단!, 속도 저하, 오류 발생 가능성 높음
    # options.add_argument('--window-size=1920,1080') # 큰 화면 크기로 더 많은 요소가 뷰포트 내에 들어올 수 있음.
    # options.add_argument("--window-size=0,0")  # 창 크기를 0으로 설정 (웹사이트의 정확한 렌더링을 보장하지 않는다.-)

    driver = webdriver.Chrome(options=options)
    
    return driver
    
