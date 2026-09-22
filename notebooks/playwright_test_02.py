from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    # 1. 브라우저 열기
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # 2. 페이지 이동
    url = "https://quotes.toscrape.com"
    page.goto(url=url)

    # 3. 페이지 가져오기
    html = page.content()

    # 4. 브라우저 닫기
    browser.close()    

    # 5. 파싱
    soup = BeautifulSoup(html, "html.parser")
    quotes = soup.find_all('div', class_='quote')

    all_quotes = []

    for div in quotes:
        all_quotes.append({
            "명언": div.find('span', class_='text').text.strip(""),
            "작가": div.find('small', class_='author').text,
            "태그" :','.join([t.text for t in div.find_all('a', class_='tag')])
        })

import pandas as pd
df = pd.DataFrame(all_quotes)
print(df)

# csv 저장 or db 에 insert
df.to_csv('quotes.csv', index=False, encoding='utf-8')
print('csv 파일 저장 완료!')