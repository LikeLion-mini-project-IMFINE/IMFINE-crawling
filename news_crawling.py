from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime
import pandas as pd
import os
from dotenv import load_dotenv
from openai import OpenAI
import json


load_dotenv(verbose=True)
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
os.environ['OPENAI_API_KEY'] = OPEN_AI_KEY


# ConnectionError 방지용 User-Agent 설정
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

# URL 입력 받기
url = input("크롤링할 뉴스 URL을 입력하세요: ")

# 결과를 담을 리스트 초기화
news_titles = []
news_contents = []
news_dates = []
news_reporter = []

# 뉴스 내용 크롤링
news = requests.get(url, headers=headers)
news_html = BeautifulSoup(news.text, "html.parser")

# 뉴스 제목 가져오기
title = news_html.select_one("#title_area > span")
if title is None:
    title = news_html.select_one("#content > div.end_ct > div > h2")

# 뉴스 기자 가져오기
reporter = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_journalist > a > em").text

# 뉴스 본문 가져오기
content = news_html.select("article#dic_area")
if not content:  # 본문이 비어있다면 다른 선택자로 대체
    content = news_html.select("#articeBody")

# 기사 텍스트만 추출
content = ''.join(str(content))

# HTML 태그 제거 및 텍스트 다듬기
pattern1 = '<[^>]*>'
title = re.sub(pattern=pattern1, repl='', string=str(title))
content = re.sub(pattern=pattern1, repl='', string=content)

# 날짜 가져오기
try:
    html_date = news_html.select_one(
        "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div:nth-child(1) > span"
    )
    news_date = html_date.attrs['data-date-time']
except AttributeError:
    news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
    news_date = re.sub(pattern=pattern1, repl='', string=str(news_date))

# 날짜 형식 맞춤
date_obj = datetime.strptime(news_date, "%Y-%m-%d %H:%M:%S")
formatted_date = date_obj.strftime("%Y-%m-%d")
print(formatted_date)

# 결과 리스트에 추가
news_titles.append(title)
news_contents.append(content)
news_dates.append(formatted_date)
news_reporter.append(reporter)

# 결과 출력
print("\n[뉴스 제목]")
print(news_titles)
print("\n[뉴스 링크]")
print(url)
print("\n[뉴스 시간]")
print(formatted_date)
print("\n[뉴스 기자]")
print(reporter)
print("\n[뉴스 본문]")
print(news_contents)

# 데이터 프레임 생성
news_df = pd.DataFrame({'date': formatted_date, 'title': news_titles, 'original_url': [url], 'reporter': news_reporter, 'full_content': news_contents})

# 데이터 저장
now = datetime.now()
news_df.to_csv('news_{}.csv'.format(now.strftime('%Y%m%d_%H시%M분%S초')), encoding='utf-8-sig', index=False)

# # Chat GPT API
# def create_chat_completion(system_input, user_input, model="gpt-4o", temperature=1.15, max_tokens=500):
#     try:
#         messages = [
#             {"role": "system", "content": system_input},
#             {"role": "user", "content": user_input}
#         ]
#
#         response = OpenAI().chat.completions.create(
#             model=model,
#             messages=messages,
#             temperature=temperature,
#             max_tokens=max_tokens
#         )
#         return response
#     except Exception as e:
#         return f"Error: {str(e)}"
#
# # 메시지 목록 예시
# system_input = "내가 아이들을 위한 금융교육 웹사이트를 만들려고 해. 경제 뉴스의 본문을 기반으로 아이들이 경제 내용을 이해하기 쉽게 설명해주고 싶어. 지피티 너가 12살정도의 아이들에게 이해하기 쉽게 설명해주는 선생님이 되어줘! 단 존댓말을 사용해줘"
# user_input = f"""
# 내가 경제 뉴스 본문을 보내줄게!
# {str(news_contents)}
# 이 내용을 기반으로 다음 지시사항을 JSON 형태에 맞추어 답변해줘:
# 1. 핵심 금융경제 키워드를 아이들의 눈높이에 맞게 설명해줘.
# 2. summary = 아이들의 눈높이에 맞게 해당 내용을 1~2줄로 요약해줘.
# 3. content = 전체 내용을 아이들의 눈높이에 맞게 설명해줘.
#
# 답변 형식:
# {{"summary": "...","content": "..."}}
# """
#
#
# # API 호출 및 결과 출력
# print("GPT API 호출")
# responses = create_chat_completion(system_input, user_input)
# print("GPT API 응답 완료")
# print(responses)
# print("===================")
#
# # content 부분 추출
# raw_content = responses.choices[0].message.content
#
# # 정규식으로 summary와 content 추출
# match = re.search(r'"summary": "(.*?)",\s*"content": "(.*?)"', raw_content, re.DOTALL)
#
# if match:
#     # JSON 데이터 생성
#     extracted_data = {
#         "summary": match.group(1),
#         "content": match.group(2)
#     }
#     # JSON 출력
#     print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
# else:
#     print("summary와 content를 찾을 수 없습니다.")