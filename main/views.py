from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django.http import HttpResponseRedirect
from django.shortcuts import render

import csv
import pandas as pd
import numpy as np
import requests
import warnings; warnings.filterwarnings('ignore')

from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from django.urls import reverse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity



# Create your views here.

test_list_df = pd.read_csv('df_last.csv', encoding='utf-8')
test_list_df2 = pd.read_csv('weather.csv', encoding='utf-8')

count = test_list_df['주소']

count_tr = []

for i in count:
    searching = i

    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(searching)
    headers = {
        "Authorization": "KakaoAK 5793cde5d6d57817d2643d29202e1b61"
    }
    count_tr.append(requests.get(url, headers=headers).json()['documents'])

# 경도를 리스트 화
x_list = []
for i in range(len(count_tr)):
    x_list.append(float(count_tr[i][0]['x']))

# 위도를 리스트 화
y_list = []
for i in range(len(count_tr)):
    y_list.append(float(count_tr[i][0]['y']))

test_list_df.loc[:, '경도'] = x_list
test_list_df.loc[:, '위도'] = y_list


def countVec():
    # CountVectorizer를 적용하기 위해 공백문자로 word 단위가 구분되는 문자열로 변환.
    count_vect = CountVectorizer(min_df=0, ngram_range=(1, 2))
    facility_mat = count_vect.fit_transform(test_list_df['태깅'])
    facility_sim = cosine_similarity(facility_mat, facility_mat)

    # 유사도가 높은 순으로 정리된 facility_sim 객체의 비교 행 위치 인덱스 값
    # 값이 높은 순으로 정렬된 비교 대상 행의 유사도 값이 아니라
    # 비교 대상 행의 위치 인덱스임에 주의
    facility_sim_sorted_ind = facility_sim.argsort()[:, ::-1]

    return facility_sim_sorted_ind


# 기존 평점을 가중 평점으로 변경하는 함수
def weighted_vote_average(record):
    C = test_list_df['평점'].mean()
    m = test_list_df['투표횟수'].quantile(0.6)

    v = record['투표횟수']
    R = record['평점']
    # (예정)날씨 관련 수식을 추가 => 실내외 구분시 활용
    return (((v / (v + m)) * R) + ((m / (v + m)) * C)) * 2


# 새롭게 정의된 평점 기준에 따라 기존 find_sim_experience 함수를 변경
def find_sim_experience(df_main, sorted_ind, title_name, top_n=10, end_idx=10):

  test_list_df['추천점수'] = test_list_df.apply(weighted_vote_average, axis=1)
  title_exp = df_main[df_main['이름'] == title_name]
  title_index = title_exp.index.values

  sim_index = sorted_ind[title_index, :top_n*3]
  sim_index = sim_index.reshape(-1)

  sim_index = sim_index[sim_index != title_index]

  return df_main.iloc[sim_index].sort_values('추천점수', ascending=False)[:end_idx]

# 우천시 추천리스트 10개 출력
def find_sim_experience_rainy(df_main, sorted_ind, title_name, top_n=10):
  test_list_df['추천점수'] = test_list_df.apply(weighted_vote_average, axis=1)
  title_exp = df_main[df_main['이름'] == title_name]
  title_index = title_exp.index.values

  sim_index = sorted_ind[title_index, :top_n*3]
  sim_index = sim_index.reshape(-1)

  sim_index = sim_index[sim_index != title_index]

  return df_main.iloc[sim_index].sort_values('추천점수', ascending=False)[:]


def input_title(input_name):
    facility_sim_sorted_ind = countVec()

    sim_exp = find_sim_experience(test_list_df, facility_sim_sorted_ind, input_name)
    sim_exp_rainy = find_sim_experience_rainy(test_list_df, facility_sim_sorted_ind, input_name)
    result_sunny = sim_exp[['이름', '주소', '추천점수', '경도', '위도']]
    result_rain = sim_exp_rainy[['이름', '주소', '추천점수', '경도', '위도']]

    # result_sunny = sim_exp[['이름', '대분류', '소분류', '실내/실외', '평점', '투표횟수', '추천점수', '경도', '위도']]
    # result_rain = sim_exp_rainy[['이름', '대분류', '소분류', '실내/실외', '평점', '투표횟수', '추천점수', '경도', '위도']]

    return result_sunny, result_rain


# 날씨기반 실내/외 판별 함수
# temper = 온도 , humid = 습도 , rain = 1시간당 강수량

def weather_choice(temper, humid, rain):
    y = humid - ((-4.3 * temper) + 147)
    if y >= 10:
        temper = temper + (y / 10)

    if rain >= 5 or temper <= 10 or temper >= 30:
        return '실내'
    else:
        return '실외'

# 기상청 API 가져와서 온도 습도 시간당 강수량을 가져와서 처리하기 위해 API에서 데이터 가져오는 코드
# REH = 습도
# T1H = 온도
# RN1 = 시간당 강수량
# 미완성 + 보여주기 위해선 날씨에 따라 실외, 실내를 구분하는 동작을 보여주기 위해
# 별도로 만든 csv 파일을 불러와 구분지었음.
# import requests
# from datetime import datetime, timedelta
# from pprint import pprint
# url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
# service_key = "OsnExmgat6fBnPcmy5/u/Ish125BWuL2gaRjXIUpbldSNUyz6obA1tlae77HEiPh67zsMKlW3nJ5MS4G/6G7jA=="
# now = datetime.now()
# if now.minute <= 40:
#     if now.hour == 0:
#         date = (now - timedelta(days=1)).strftime('%Y%m%d')
#         date = '2300'
#     else:
#         date = now.strftime('%Y%m%d')
#         time = (now - timedelta(hours=1)).strftime('%H00')
# else:
#     date = base_date = now.strftime('%Y%m%d')
#     time = now.strftime('%H00')
# params = {
#     'serviceKey': service_key,
#     'numOfRows': 30,
#     'pageNo': 1,
#     'dataType': 'JSON',
#     'base_date': date,
#     'base_time': time,
#     'nx': 59,
#     'ny': 74
# }
# res = requests.get(url=url, params=params)
# data = res.json()
# data = data['response']['body']['items']['item']
# pprint(data)


def run_model(input_name, weather=0):
    # weather = 맑음 : 0 (default) / 비 : 1

    result_sunny, result_rain = input_title(input_name)

    # 날씨로 실내/실외 필터링

    temper = test_list_df2.loc[weather][0:][0]  # 온도
    humid = test_list_df2.loc[weather][0:][1]  # 습도
    rain = test_list_df2.loc[weather][0:][2]  # 강수량

    # 비 -> 실내만 추천
    if weather_choice(temper, humid, rain) == "실내":
        return result_rain[result_rain['실내/실외'] == "실내"][:10]

        # 맑음 -> 실내/외 모두 추천
    else:
        return result_sunny


# def hello_world(request, a = '양동시장'):
#
#     # print(test_list_df)    ## 위,경도 더해진 csv 확인용 코드
#
#     choice_df = run_model(a)
#
#     choice_df_list = choice_df.values.tolist()
#     print(choice_df_list)
#     # print(choice_df)
#
#     return render(request, 'accountapp/hello_world.html', context={'choice_df_list': zip(choice_df_list)})

class FirstView(TemplateView):
    template_name = 'main/second_Page.html.html'




class SecondView(TemplateView):
    template_name = 'main/second_Page.html'

    def get(self, request):
        title = '양동시장'
        data = run_model(title)
        data_list = data.values.tolist()

        context = {'title': title, 'data': zip(data_list)}
        return render(request, 'main/second_Page.html', context=context)
#
# def hello_world(request):
#     test_list = pd.read_csv('df_test.csv', encoding='utf-8')
