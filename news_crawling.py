from bs4 import BeautifulSoup
import requests
import re
import datetime
import pandas as pd

# ConnectionError 방지용 User-Agent 설정
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

# 크롤링 대상 URL (하나의 URL만 사용)
url = "https://n.news.naver.com/mnews/article/081/0003497000"

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

# 결과 리스트에 추가
news_titles.append(title)
news_contents.append(content)
news_dates.append(news_date)
news_reporter.append(reporter)

# 결과 출력
print("\n[뉴스 제목]")
print(news_titles)
print("\n[뉴스 링크]")
print(url)

# 데이터 프레임 생성
news_df = pd.DataFrame({'date': news_dates, 'title': news_titles, 'original_url': [url], 'reporter': news_reporter, 'full_content': news_contents})

# 데이터 저장
now = datetime.datetime.now()
news_df.to_csv('news_{}.csv'.format(now.strftime('%Y%m%d_%H시%M분%S초')), encoding='utf-8-sig', index=False)