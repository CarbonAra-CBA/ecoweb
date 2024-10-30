from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

# 현재 작업 디렉토리의 절대 경로 가져오기
current_dir = os.path.abspath(os.path.dirname(__file__))
# HTML 파일의 경로 설정
html_path = os.path.join(current_dir, 'templates', 'index.html')
# file:// 프로토콜을 사용하여 로컬 파일 URL 생성
file_url = f"file:///{html_path}"

# Chrome 옵션 설정
chrome_options = Options()
# chrome_options.add_argument('--headless')  # 브라우저를 띄우지 않고 실행하려면 이 옵션 활성화

# WebDriver 설정
service = Service('chromedriver의_경로')  # chromedriver 경로 지정
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 페이지 로드
    driver.get(file_url)
    
    # 잠시 대기 (페이지 로딩을 위해)
    driver.implicitly_wait(2)
    
    # 스크린샷 저장
    driver.save_screenshot('file_screenshot.png')
    print("스크린샷이 저장되었습니다!")

finally:
    # 브라우저 종료
    driver.quit()