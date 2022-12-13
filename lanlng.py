#!/usr/bin/env python
# coding: utf-8

# In[34]:


import requests
import MySQLdb


conn = MySQLdb.connect(host='localhost', db='map', user='min', passwd='pass', charset='utf8mb4')
c = conn.cursor()

client_id = "w0lbb7bbke"
client_secret = "RpEuKcxoaUvE76bClqLuFwTe6OqBU8XjXyGHipZA"

def geocoding(addr):
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query={addr}"
    headers = {'X-NCP-APIGW-API-KEY-ID': client_id,
               'X-NCP-APIGW-API-KEY': client_secret
               }

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()
        lat = data['addresses'][0]['y']  # 위도
        lng = data['addresses'][0]['x']  # 경도
        stAddress = data['addresses'][0]['roadAddress'] # 도로명 주소
        list = [lat,lng,stAddress]
        return list

seoul = ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구']

for i in seoul:
    sql = f'select address, id from restaurant where id like "{i}%"'
    c.execute(sql)
    result = c.fetchall()
    for add in result:
        arr = geocoding(add[0])
        c.execute("INSERT INTO location VALUES (%s, %s, %s)", (add[1], arr[0], arr[1]))
    conn.commit()

