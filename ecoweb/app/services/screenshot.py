import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def capture_screenshot(url, output_path, is_file= False):
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')  # 화면 크기 설정

    driver = webdriver.Chrome(options=chrome_options)
    
    try: 
        if is_file:
            file_url = f"file://{url}"
            driver.get(file_url)
        else:
            driver.get(url)
        
        time.sleep(2)

        # 전체 페이지 높이 계산
        height = driver.execute_script("return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
        
        # 뷰포트 크기 설정
        driver.set_window_size(1920, height)
        
        # 스크린샷 촬영
        driver.save_screenshot(output_path)
        return True

    except Exception as e:
        print(f"Screenshot capture failed: {str(e)}")
        return False
    
    finally:
        driver.quit()
