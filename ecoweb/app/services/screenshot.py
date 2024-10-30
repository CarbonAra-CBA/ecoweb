import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import os
from local_server import LocalServer

def capture_screenshot(url, output_path, is_file= False):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')  # 화면 크기 설정

    driver = webdriver.Chrome(options=chrome_options)
    
    server = None
    try: 
        if is_file:
    
            # 파일이 있는 디렉로티의 루트 경로 찾기
            file_dir = os.path.dirname(os.path.abspath(url))
            print(f"File directory: {file_dir}")
            root_dir = os.path.dirname(file_dir)
            print(f"Root directory: {root_dir}")
            # Local 서버 시작
            server = LocalServer(root_dir)
            server.start()

            # 도메인 추출하여 로컬 서버 URL 생성
            domain = os.path.basename(file_dir)
            print(f"Domain: {domain}")
            local_url = f"http://localhost:8000/{domain}/index.html"

            print(f"Accessing local URL : {local_url}")
            driver.get(local_url)

        else:
            driver.get(url)
        
        driver.implicitly_wait(10)
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        driver.set_window_size(1920, height)
        # 스크린샷 촬영
        driver.save_screenshot(output_path)
        print(f"Screenshot saved to {output_path}")
        image = Image.open(output_path)
        image.show()
        return True

    except Exception as e:
        print(f"Screenshot capture failed: {str(e)}")
        return False
    
    finally:
        driver.quit()
        if server:
            server.stop()
