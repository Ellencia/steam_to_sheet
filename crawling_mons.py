import time
import random
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 피하기
options.add_argument("--start-maximized")  # 최대화된 화면으로 실행

# 크롬 브라우저 열기
driver = webdriver.Chrome(options=options)
driver.get('https://monsnode.com/search.php?search=ikejyo%20yuri')

# 페이지가 로드될 때까지 대기 (예: CAPTCHA가 나타날 때까지)
try:
    # 예시: 버튼이 나타날 때까지 최대 10초 기다림
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='submit']")))  # 수정된 XPATH 사용

    # 사람처럼 마우스와 클릭 동작
    def move_and_click(element):
        actions = ActionChains(driver)

        # 마우스를 천천히 이동시키기 (move_by_offset 사용)
        x_offset = random.randint(-5, 5)
        y_offset = random.randint(-5, 5)

        # move_by_offset을 사용하여 마우스를 조금씩 이동
        for _ in range(10):  # 조금씩 이동하는 루프
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.05, 0.1))  # 자연스러운 지연

        # 클릭하기
        actions.click().perform()

    # 버튼 클릭 (예시)
    move_and_click(button)

    # 잠시 대기 (사람처럼 행동하기 위해 시간 지연)
    time.sleep(random.uniform(3, 5))

    # 스크롤: 사람처럼 스크롤을 조금씩 하여 페이지 탐색
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(random.uniform(1, 3))

    # 추가적으로 필요한 입력값을 채우는 부분 예시
    input_box = driver.find_element(By.XPATH, "//input[@name='username']")
    input_box.send_keys("exampleUsername")
    time.sleep(random.uniform(1, 2))
    input_box.send_keys("examplePassword")
    time.sleep(random.uniform(1, 3))
    input_box.send_keys(Keys.RETURN)

    # 캡챠 인증을 수동으로 처리하도록 대기
    print("캡챠 인증을 완료한 후 Enter 키를 눌러 계속 진행하세요.")
    input()  # 사용자가 캡챠 인증을 완료할 때까지 대기

    # 페이지 대기
    time.sleep(random.uniform(2, 4))

except Exception as e:
    print("오류 발생:", e)

finally:
    # 테스트 종료 후 브라우저 닫기
    driver.quit()
