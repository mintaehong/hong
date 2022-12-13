
import requests
import MySQLdb

# MySQL 서버 접속
conn = MySQLdb.connect(host='localhost', db='map', user='min', passwd='pass', charset='utf8mb4')
c = conn.cursor()

# 네이버 지도 API 인증
client_id = "w0lbb7bbke"
client_secret = "RpEuKcxoaUvE76bClqLuFwTe6OqBU8XjXyGHipZA"
# 네이버 지도 API를 이용하여 주소로 위도와 경도를 불러오는 함수
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

# restaurant테이블의 주소와 ID를 가져옴
sql = 'select address, id from restaurant"'
c.execute(sql)
result = c.fetchall()
# gecodingo 함수에 주소를 넘겨주고 실행
for values in result:
    arr = geocoding(values[0])
    # ID와 위도, 경도 
    c.execute("INSERT INTO location VALUES (%s, %s, %s)", (values[1], arr[0], arr[1]))
conn.commit()

