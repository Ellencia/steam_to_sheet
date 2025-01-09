from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def fetch_redirect_links(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    links = []
    for a_tag in soup.select('div.listn a[href*="redirect.php"]'):
        href = a_tag['href']
        if href.startswith('https://monsnode.com/redirect.php'):
            links.append(href)
    return links

def main():
    # Selenium WebDriver 설정
    options = Options()
    options.add_argument("--headless")  # 브라우저 창을 열지 않음
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service("/path/to/chromedriver")  # 크롬 드라이버 경로 설정
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # 사이트 접속
        url = "https://monsnode.com/search.php?search=ikejyo%20yuri"
        print("Loading page...")
        driver.get(url)
        time.sleep(5)  # 페이지 로딩 대기
        
        # 페이지 소스 가져오기
        page_source = driver.page_source
        print("Fetching redirect links...")
        
        # 링크 추출
        redirect_links = fetch_redirect_links(page_source)
        print(f"Found {len(redirect_links)} redirect links.")
        
        # 파일에 저장
        with open("video_links.txt", "w", encoding="utf-8") as f:
            for link in redirect_links:
                f.write(link + "\n")
        
        print(f"Saved {len(redirect_links)} video URLs to video_links.txt")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
