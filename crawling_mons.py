import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://monsnode.com/search.php?search=ikejyo%20yuri"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_redirect_links(base_url):
    """HTML에서 중간 redirect.php 링크 추출"""
    response = requests.get(base_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    redirect_links = [
        a_tag["href"]
        for a_tag in soup.find_all("a", href=True)
        if "redirect.php" in a_tag["href"]
    ]
    return redirect_links

def get_video_url(redirect_url):
    """redirect 링크를 따라가 최종 비디오 URL 추출"""
    try:
        response = requests.get(redirect_url, headers=HEADERS, timeout=10, allow_redirects=True)
        if "video.twimg.com" in response.url:
            return response.url
    except requests.exceptions.RequestException as e:
        print(f"Error fetching video URL: {e}")
    return None

def main():
    redirect_links = get_redirect_links(BASE_URL)
    print(f"Found {len(redirect_links)} redirect links.")

    video_urls = []
    for idx, redirect in enumerate(redirect_links, start=1):
        print(f"[{idx}] Processing: {redirect}")
        video_url = get_video_url(redirect)
        if video_url:
            print(f"Video URL: {video_url}")
            video_urls.append(video_url)
        else:
            print("Failed to fetch video URL.")
        time.sleep(1)  # 요청 간 딜레이

    # 최종 비디오 URL 출력 또는 저장
    with open("video_links.txt", "w") as file:
        for url in video_urls:
            file.write(url + "\n")

    print(f"Saved {len(video_urls)} video URLs to video_links.txt")

if __name__ == "__main__":
    main()
