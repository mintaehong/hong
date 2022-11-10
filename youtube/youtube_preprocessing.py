import pandas as pd
import numpy as np
import os
import re
from datetime import datetime

# 결측치 제거 함수
def pre(column):
    global youtube_50_table_all_pre
    table = youtube_50_table_all_pre['제목'][youtube_50_table_all_pre[column].isnull()].unique()

    # 같은 영상 중 가장 가까운 아래 값으로 변경
    for title in table:
        youtube_50_table_all_pre[column][youtube_50_table_all_pre['제목'] == title] = youtube_50_table_all_pre[column][youtube_50_table_all_pre['제목'] == title].fillna(method='bfill')

    table = youtube_50_table_all_pre['제목'][youtube_50_table_all_pre[column].isnull()].unique()

    # 같은 영상 중 가장 가까운 위 값으로 변경
    for title in table:
        youtube_50_table_all_pre[column][youtube_50_table_all_pre['제목'] == title] = youtube_50_table_all_pre[column][youtube_50_table_all_pre['제목'] == title].fillna(method='ffill')
    # 위아래 전부 없다면 제거
    youtube_50_table_all_pre = youtube_50_table_all_pre.dropna(subset = [column])
    return youtube_50_table_all_pre


# 데이터 프레임 생성
youtube_50_table_all = pd.DataFrame(columns=['제목','조회수','좋아요수','게시날', '영상길이', '댓글수',  '유튜버', '유튜버구독자수'])

# 저장된 데이터 6시간 간격으로 데이터 추출 (6시간 간격 이하로는 차이가 적기 때문에)
day = []
file_list = os.listdir('C://Users/min/youtube_use')
for name in file_list:
    if name[26:28] in ('00', '06', '12', '18') and name.find('clean') == -1:
        table = pd.read_csv(f'youtube_use/{name}')
        # 추출날 데이터
        for roof in range(table.shape[0]):
            day.append(name[15:25])
        youtube_50_table_all = youtube_50_table_all.append(table, ignore_index=True)

# 필요없는 컬럼 제거
youtube_50_table_all.drop(columns="영상설명",inplace=True)

# 필요한 컬럼 추가
youtube_50_table_all['추출날'] = day

# 결측치 제거 ---------------------------------------------------------------------------------------------------------------------

# 제목 결측치 제거
youtube_50_table_all_pre = youtube_50_table_all.dropna(subset = ['제목'])

# 모든 컬럼 결측치 제거
for i in youtube_50_table_all.columns:
    youtube_50_table_all_pre = pre(i)

# 전처리 ------------------------------------------------------------------------------------------------------------------

# 조회수 천 단위 정수로 변경
youtube_50_table_all_pre['조회수'] = ((youtube_50_table_all_pre['조회수'].str.replace('조회수', '').str.replace(',', '').str.replace('만', '0000').str.replace('회', '').str.strip()).astype(float)/10000)
youtube_50_table_all_pre['조회수'][youtube_50_table_all_pre['조회수'] < 1] = youtube_50_table_all_pre['조회수'][youtube_50_table_all_pre['조회수'] < 1]*10000
youtube_50_table_all_pre['조회수'] = youtube_50_table_all_pre['조회수'].astype(int)

# 좋아요수 비공개 동영상 제거
youtube_50_table_all_pre.drop(index = youtube_50_table_all_pre[youtube_50_table_all_pre['좋아요수'] == '좋아요'].index, inplace=True)

# 좋아요수 천 단위 정수로 변경
youtube_50_table_all_pre['좋아요수'] = youtube_50_table_all_pre['좋아요수'].str.replace('\n이 동영상이 마음에 듭니다.','')
likes = []
for like in youtube_50_table_all_pre['좋아요수']:
    if like[-1:] == '만':
        likes.append(float(like.replace('만', ''))*10000)
    elif like[-1:] == '천':
        likes.append(float(like.replace('천', ''))*1000)
    else:
        likes.append(float(like))
youtube_50_table_all_pre['좋아요수'] = likes
youtube_50_table_all_pre['좋아요수'] = (youtube_50_table_all_pre['좋아요수']/1000).astype(int)

# 게시날 경과날 정수로 변경
time = []
for date in youtube_50_table_all_pre['게시날']:
    # ~시간 전 올라온 동영상은 경과날 0으로 처리
    if date.find('시간') > 0:
        date = '0'
    time.append(date.replace('days', '').replace('일 전', '').strip())

youtube_50_table_all_pre['게시날'] = time

## - 영상 길이 초단위로 변경
r_time = []
for run_t in youtube_50_table_all_pre['영상길이'].str.split(':'):
    if len(run_t) == 3:
        r_time.append((int(run_t[0])*3600)+(int(run_t[1])*60)+int(run_t[2]))
    else:
        r_time.append((int(run_t[0])*60)+int(run_t[1]))
youtube_50_table_all_pre['영상길이'] = r_time

# 댓글 수 정수로 변경
youtube_50_table_all_pre['댓글수'] = youtube_50_table_all_pre['댓글수'].str.replace('댓글', '').str.replace('개', '').str.replace(',', '').str.strip()

# 유튜버 구독자 수 천 단위 정수로 변경
y_count = []
for count in youtube_50_table_all_pre['유튜버구독자수'].str.replace('구독자', '').str.strip():
    if count.find('천명') > 0:
        count = count.replace('천명', '')
        y_count.append((float(count.replace('천명', '')) * 1000)/1000)
    else:
        count = count.replace('만명', '')
        y_count.append((float(count) * 10000)/1000)
youtube_50_table_all_pre['유튜버구독자수'] = y_count
youtube_50_table_all_pre['유튜버구독자수'] = youtube_50_table_all_pre['유튜버구독자수'].astype(int)

# 제목점수 추가 (자주쓰는 단어일수록 점수가 올라가는 구조)
# 특수기호 제거 목적
cp1 = re.compile(r'[^\w\s]')
# 한글, 영어, 숫자로 이루어진 단어로 나누기 위함
cp2 = re.compile('[가-힣A-z0-9]+')
# 조사제거 목적
josa = ['께서', '에서', '을', '를', '이가', '에게', '께', '한테', '에게서', '로서', '로써', '랑', '만큼', '이다', '는', '부터', '로부터', '으로부터', '까지','의','으로']
# 제목을 단어로 나누어 저장
title_word = []
for title in youtube_50_table_all_pre['제목'].unique():
    title_cp = cp1.sub('', title)
    for jo in josa:
        title_cp = title_cp.replace(jo, '')
    for ti in cp2.findall(title_cp):
        if len(ti) > 1:
            title_word.append(ti)
# 나누어진 단어 중복된 개수 구함 (중복된 개수만큼 점수)
word_count = {}
for word in title_word:
    word_count[word] = 0
for word in title_word:
    word_count[word] += 1
# 사용하기 편하게 시리즈로 변환
title_word_count = pd.Series(word_count)
# 제목에 단어 포함되어있으면 점수 추가 (점수는 30위까지 사용)
title_point = []
for title in youtube_50_table_all_pre['제목']:
    point = 0
    for i in title_word_count.sort_values(ascending = False).head(30).index:
        if  i in title:
            point += title_word_count[i]
    title_point.append(point)
# 제목점수 칼럼추가
youtube_50_table_all_pre['제목점수'] = title_point

youtube_50_table_all_pre = youtube_50_table_all_pre.astype({'게시날':int, '댓글수':int})

# csv파일로 저장
youtube_50_table_all_pre.to_csv(f'youtube_50_table_pre.csv', index=False, encoding='utf8')
