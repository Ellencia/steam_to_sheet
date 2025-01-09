from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 기본 설정
BASE_URL = "https://monsnode.com/search.php?search=ikejyo%20yuri"
HEADLESS = False  # True로 설정하면 브라우저가 표시되지 않음

# 크롬 드라이버 초기화 함수
def init_driver(headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

# 리다이렉트 링크 추출 함수
def fetch_redirect_links(base_url):
    driver = init_driver(HEADLESS)
    try:
        print("Loading page...")
        driver.get(base_url)

        # 페이지의 특정 요소가 로드될 때까지 대기
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )

        print("Fetching redirect links...")
        # 모든 <a> 태그 가져오기
        links = driver.find_elements(By.TAG_NAME, "a")
        redirect_links = [
            link.get_attribute("href")
            for link in links
            if link.get_attribute("href") and "redirect.php" in link.get_attribute("href")
        ]
        print(f"Found {len(redirect_links)} redirect links.")
        return redirect_links
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        driver.quit()

# 비디오 URL 저장 함수
def save_video_urls(video_urls, filename="video_links.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(video_urls))
    print(f"Saved {len(video_urls)} video URLs to {filename}.")

# 메인 함수
def main():
    # 리다이렉트 링크 가져오기
    redirect_links = fetch_redirect_links(BASE_URL)
    if not redirect_links:
        print("No redirect links found.")
        return

    # 비디오 URL 추출
    video_urls = redirect_links

    # 비디오 URL 저장
    save_video_urls(video_urls)

if __name__ == "__main__":
    main()
