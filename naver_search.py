
import MySQLdb
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

# MySQL 서버 접속
conn = MySQLdb.connect(host='localhost', db='map', user='min', passwd='pass', charset='utf8mb4')
c = conn.cursor()

# 서울 25개 구 리스트 저장
seoul = ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구']

for input_ in seoul:
    # 크롬 드라이버 설정
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--window-size=1920x1080')
    driver = webdriver.Chrome('C:/Users/min/chromedriver.exe', options=chrome_options)
    action = ActionChains(driver)
    driver.get('https://map.naver.com/v5/')
    sleep(3)
    # 검색어 입력
    query = driver.find_element(By.CSS_SELECTOR,'#container > shrinkable-layout > div > app-base > search-input-box > div > div.search_box > div > input')
    query.send_keys(f'{input_} 맛집')
    query.send_keys(Keys.ENTER)
    sleep(5)
    # restaurant 테이블의 id를 위한 변수
    idx = 0
    # 음식점 클릭을 위한 변수
    idx_1 = 1
    # XPATH를 변경하기 위한 변경
    idx_3 = 0
    while True:
        try:
            idx += 1
            # 새로운 프레임으로 변경
            driver.switch_to.default_content()
            element = driver.find_element(By.ID,"searchIframe")
            driver.switch_to.frame(element)
            sleep(2)
            # 음식점 클릭
            # idx_3이 증가하면 XPATH 변경
            if idx_3 == 0:
                driver.find_element(By.XPATH, f'//*[@id="_pcmap_list_scroll_container"]/ul/li[{idx_1}]/div[1]/a/div/div/span[1]').click()
                name = driver.find_element(By.XPATH, f'//*[@id="_pcmap_list_scroll_container"]/ul/li[{idx_1}]/div[1]/a/div/div/span[1]').text
            else:
                driver.find_element(By.XPATH, f'//*[@id="_pcmap_list_scroll_container"]/ul/div[{idx_3}]/li[{idx_1}]/div[1]/a/div/div/span[1]').click()
                name = driver.find_element(By.XPATH, f'//*[@id="_pcmap_list_scroll_container"]/ul/div[{idx_3}]/li[{idx_1}]/div[1]/a/div/div/span[1]').text
            # 새로운 프레임으로 변경
            sleep(1)
            driver.switch_to.default_content()
            element2 = driver.find_element(By.ID, "entryIframe")
            driver.switch_to.frame(element2)
            sleep(2)
            # 음식점 정보 추출
            try:
                star = float(driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[2]/div[1]/div[2]/span[1]/em').text)
            except:
                star = None
            category = driver.find_element(By.XPATH, '//*[@id="_title"]/span[2]').text
            location = driver.find_element(By.XPATH, '//*[@class="IH7VW"]').text
            try:
                phone = driver.find_element(By.XPATH, '//*[@class="dry01"]').text
            except:
                phone = None
            visitor_review = driver.find_element(By.XPATH, '//*[contains(text(), "방문자리뷰")]/em').text
            blog_review = driver.find_element(By.XPATH, '//*[contains(text(), "블로그리뷰")]/em').text
            sleep(1)
            # 음식정 정보 INSERT
            c.execute("INSERT INTO restaurant VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (f'{input_}-{idx}', name, category, star, int(visitor_review.replace(',', '')), int(blog_review.replace(',', '')), location, phone))
            # 메뉴 클릭 (메뉴 창이 없을 경우 넘어감)
            try:
                driver.find_element(By.XPATH, '//span[contains(text(), "메뉴")]').click()
            except:
                idx_1 += 1
                continue
            sleep(3)
            # 메뉴 추출을 위한 변수
            idx_2 = 1
            # 메뉴 정보 추출
            while True:
                try:
                    menu = driver.find_element(By.XPATH, f'//*[@class="ZUYk_"]/li[{idx_2}]//*[@class="Sqg65"]').text
                    price = driver.find_element(By.XPATH, f'//*[@class="ZUYk_"]/li[{idx_2}]//*[@class="SSaNE"]').text
                    # 메뉴 정보 INSERT
                    c.execute("INSERT INTO menu(r_id, menu, price) VALUES (%s, %s, %s)", (f'{input_}-{idx}', menu, int(price.replace(',', '').replace('원', ''))))
                    idx_2 += 1
                # 메뉴 더보기 클릭
                except:
                    try:
                        driver.find_element(By.XPATH, f'//*[@id="app-root"]/div/div/div/div[7]/div/div[1]/div[2]/a').click()
                        sleep(2)
                    except:
                        idx_1 +=1
                        break
            # 리뷰 정보 추출
            try:
                driver.find_element(By.XPATH, '//*[@id="app-root"]/div/div/div/div[5]/div/div/div/div/a/span[contains(text(), "리뷰")]').click()
                sleep(3)
                for i in range(1,5):
                    advantages=driver.find_element(By.XPATH, f'//*[@class="uNsI9"]/li[{i}]/div[2]/span[1]').text
                    a_count=driver.find_element(By.XPATH, f'//*[@class="uNsI9"]/li[{i}]/div[2]/span[2]').text
                    # 리뷰 정보 추출
                    c.execute("INSERT INTO r_character(r_id, advantages, count) VALUES (%s, %s, %s)", (f'{input_}-{idx}', advantages, int(a_count.split('\n')[1])))
            except:
                pass
        except:
            idx_3 += 1
            # 더이상 음식점이 없을 때 break
            try:
                action.move_to_element(driver.find_element(By.XPATH, f'//*[@id="_pcmap_list_scroll_container"]/ul/div[{idx_3}]')).perform()
            except:
                break
            idx_1 = 1
            sleep(3)
    driver.quit()
    conn.commit()
conn.close()
