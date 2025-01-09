from bs4 import BeautifulSoup

# HTML 파일 경로
html_file_path = 'monsnodehtml.txt'
output_file_path = 'video_links.txt'

# HTML 파일 열기
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# BeautifulSoup을 사용하여 HTML 파싱
soup = BeautifulSoup(html_content, 'html.parser')

# 'a' 태그 중 href 속성에 'redirect.php'가 포함된 링크만 추출
redirect_links = [a['href'] for a in soup.find_all('a', href=True) if 'redirect.php' in a['href']]

# 추출된 링크들을 video_links.txt에 저장
with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for link in redirect_links:
        output_file.write(link + '\n')

print(f"Links have been saved to {output_file_path}")
