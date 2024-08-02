import chromedriver_autoinstaller
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class Driver:

    def init_driver(self):
        # 크롬 드라이버 자동 설치
        chromedriver_autoinstaller.install()

        # 크롬 옵션 설정
        options = Options()
        options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        options.add_argument('--headless')  # 브라우저를 표시하지 않고 실행
        options.add_argument('--disable-web-security')  # CORS 정책 우회 설정
        options.add_argument('--ignore-certificate-errors')  # SSL 인증서 무시 설정
        # 로그 수준 설정
        options.add_argument('--log-level=3')  # 3: ERROR

        # 드라이버 초기화
        driver = webdriver.Chrome(options=options) # 초기화(드라이버 시작 browser session start!)
        driver.set_page_load_timeout(60)  # 페이지 로드 타임아웃 60초 설정 (60초가 지나면 에러 발생)

        return driver


