import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://monsnode.com/search.php?search=ikejyo%20yuri"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_redirect_links(base_url):
    """중간 링크 (redirect.php) 추출"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    response = session.get(base_url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    redirect_links = [
        a_tag["href"]
        for a_tag in soup.find_all("a", href=True)
        if "redirect.php" in a_tag["href"]
    ]
    return redirect_links

def get_video_url(redirect_url):
    """redirect 링크로부터 최종 영상 URL 얻기"""
    response = requests.get(redirect_url, headers=HEADERS, timeout=10, allow_redirects=True)
    return response.url

def main():
    redirect_links = get_redirect_links(BASE_URL)
    print(f"Found {len(redirect_links)} redirect links.")

    for idx, redirect in enumerate(redirect_links, start=1):
        try:
            print(f"[{idx}] Processing: {redirect}")
            video_url = get_video_url(redirect)
            print(f"Video URL: {video_url}")
            time.sleep(2)  # 요청 간 딜레이
        except Exception as e:
            print(f"Failed to process {redirect}: {e}")

if __name__ == "__main__":
    main()
