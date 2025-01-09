import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 쿠키를 txt 파일에서 읽어서 적용하는 함수
def load_cookies(driver, cookie_file):
    # txt 파일에서 쿠키를 읽어옴
    with open(cookie_file, 'r', encoding='utf-8') as file:
        cookies = json.load(file)  # JSON 형식으로 읽기

    # 쿠키들을 driver에 추가
    for cookie in cookies:
        # expirationDate를 expiry로 변경
        if 'expirationDate' in cookie:
            cookie['expiry'] = int(cookie['expirationDate'])  # UNIX 타임스탬프로 변환
        
        # 'sameSite' 값이 없거나 'unspecified'인 경우 'Lax'로 설정
        if 'sameSite' not in cookie or cookie['sameSite'] == 'unspecified':
            cookie['sameSite'] = 'Lax'

        # 쿠키 추가
        driver.add_cookie(cookie)

# Selenium WebDriver 설정
def create_driver():
    options = Options()
    options.add_argument("user-data-dir=C:/path/to/your/chrome/profile")  # 프로필 경로
    driver = webdriver.Chrome(options=options)

    return driver

def main():
    # 크롬 드라이버 생성
    driver = create_driver()

    # 크롬 브라우저에서 이미 로그인된 세션이 있을 경우 쿠키 로드
    driver.get("https://monsnode.com/")  # 임의의 페이지로 접속해서 쿠키 추가
    time.sleep(5)  # 로딩 대기

    # 쿠키 로드 함수 호출
    load_cookies(driver, "cookies.txt")  # 쿠키가 저장된 txt 파일 경로

    # 쿠키가 적용된 후 해당 페이지로 다시 접속
    driver.refresh()  # 새로 고침
    time.sleep(5)
    input("\nPress Enter to continue")
    
    # 예시로 특정 페이지로 이동 후 작업을 계속할 수 있음
    driver.get("https://monsnode.com/search.php?search=ikejyo%20yuri")
    time.sleep(5)  # 페이지 로딩 대기

    # 페이지 소스 가져오기
    page_source = driver.page_source
    print("Fetching redirect links...")
    print(page_source)

    # 필요한 추가 작업을 할 수 있습니다.

    # 세션 종료
    driver.quit()

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
