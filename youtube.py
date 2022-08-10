import os
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep
from pyvirtualdisplay import Display

## 리눅스 환경에서 실행되기 때문에 리눅스 환경에 최적화 설정
display = Display(visible=0, size=(1920, 1080))
display.start()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--single-process")
chrome_options.add_argument('--window-size=1920x1080')
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36")

# 유튜브 인기 급상승 동영상 주소
url = 'https://www.youtube.com/feed/explore'

# 크롬 실행
driver = webdriver.Chrome('/root/chromedriver', chrome_options=chrome_options)
sleep(3)
driver.get(url)
sleep(5)

# 외국 서버로 잡혀있기 때문에 한국으로 국가 변경.
driver.find_element(By.CSS_SELECTOR, '#buttons > ytd-topbar-menu-button-renderer:nth-child(2)').click()
sleep(3)
driver.find_element(By.CSS_SELECTOR, '#right-icon').click()
sleep(1)
driver.find_element(By.XPATH, '//*[@id="items"]/ytd-compact-link-renderer[83]').click()
sleep(5)

# 실행시 서버 CPU, 메모리 사용량이 많아 에러가 자주 발생 에러를 잡아주기 위한 변수
error = 0

# 영상 정보 리스트
youtube_info = []

for idx in range(1, 51):

    # 에러 발생시 크롬 재실행
    if error == 1:
        driver.quit()
        driver = webdriver.Chrome('/root/chromedriver', chrome_options=chrome_options)
        sleep(3)
        driver.get(url)
        sleep(5)
        driver.find_element(By.CSS_SELECTOR, '#buttons > ytd-topbar-menu-button-renderer:nth-child(2)').click()
        sleep(1)
        driver.find_element(By.CSS_SELECTOR, '#right-icon').click()
        sleep(1)
        driver.find_element(By.XPATH, '//*[@id="items"]/ytd-compact-link-renderer[83]').click()
        sleep(5)
        error = 0
    sleep(7)

    # 정보 추출
    views = driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) #metadata-line > span:nth-child(1)').text
    up_date = driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) #metadata-line > span:nth-child(2)').text
    title = driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) yt-formatted-string').text
    youtuber = driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) ytd-channel-name a').text
    running_time = driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) span').text

    # 유독 조회수를 찾지 못하는 에러가 있어서 에러시 재실행시킴
    if views == '':
        idx -= 1
        error = 1
        continue

    # 동영상 클릭시 추출 할 수 있는 정보가 있기 때문에 동영상 클릭
    # 셀렉터가 윈도우 화면에 잡혀있지 않으면 에러 발생하여 보일때까지 스크롤 내림
    for i in range(10):
        try:
            driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) h3').click()
        except:
            driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        if driver.current_url != url:
            break
    sleep(10)
    likes = driver.find_element(By.XPATH, '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer[1]/a').text

    # 정보가 화면 아래있기 때문에 스크롤 내림
    driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    sleep(5)

    # 댓글을 막아놓은 동영상일 경우 0으로 처리
    try:
        comment_c = driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string').text
    except:
        comment_c = '0'
    youtuber_sub = driver.find_element(By.XPATH, '//*[@id="owner-sub-count"]').text
    driver.back()
    sleep(5)
    running_time = driver.find_element(By.CSS_SELECTOR, f'#grid-container > ytd-video-renderer:nth-child({idx}) span').text

    # 동영상 정보 저장
    youtube_info.append([title,views,likes,up_date, running_time, comment_c, youtuber, youtuber_sub])

driver.quit()

# 데이터 프레임으로 변환
youtube_table = pd.DataFrame(youtube_info, columns=['제목','조회수','좋아요수','게시날', '영상길이', '댓글수', '유튜버', '유튜버구독자수'])

# 날짜와 시간을 활용하여 파일 이름 저장
now = datetime.now()
time = now.time()
now_date = f'{now.date()}_{time.strftime("%H")}시{time.strftime("%m")}분'
youtube_table.to_csv(f'/root/min/youtube_hot_50_{now_date}.csv', index=False, encoding='utf8')
