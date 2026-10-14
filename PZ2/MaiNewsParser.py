import sqlite3
import os
import urllib3
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime

def ParsPage(page, news_data):
    url = f'https://mai.ru/press/news/?tags=1235&PAGEN_1={page}'
    response = session.get(url, verify=False)
    if response.status_code==200:
        html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    news_items = soup.find_all('article')

    for item in news_items:
        title = item.find('h5').text  
        
        link = 'https://mai.ru/press/news/' + item.find_parent('a').get('href', '')

        date_tag = item.find('span', class_='badge')
        date = date_tag.get_text()
        if date[-2]!='2':
            date += ' 2026'
        if date[1]==' ':
            date = '0'+ date
        date = date.replace('янв','01',1).replace('фев','02',1).replace('мар','03',1).replace('апр','04',1).replace('мая','05',1).replace('июн','06',1).replace('июл','07',1).replace('авг','08',1).replace('сен','09',1).replace('окт','10',1).replace('ноя','11',1).replace('дек','12',1)
        date = date.replace(' ','.',2)
        news_data.append([title, date, link])
    return news_data

db_file_name='news_mai.db'

# Отключаем предупреждения о небезопасном SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False  # Отключаем проверку для всей сессии

# Подключение к файлу бд (создаётся автоматически, если не существует)
conn = sqlite3.connect(db_file_name)
cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
    ("news",)
)
table_exists = cursor.fetchone() is not None

if not table_exists:
    cursor.execute('''
        CREATE TABLE news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            link TEXT NOT NULL,
            detect_time TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()

    news_data=[]
    # с 2 чтобы повторным запуском проверить блок else с добавлением "новых" ноновостей
    for page in range(1,10):
        ParsPage(page, news_data)
        time.sleep(1)

    for new in news_data[::-1]:
        cursor.execute(
            "INSERT INTO news (title, date, link, detect_time, category) VALUES (?, ?, ?, ?, ?)",
            (new[0], new[1], new[2], datetime.now(), "Наука")
        )
        conn.commit()
else:
    cursor.execute("""
        SELECT * FROM (
            SELECT * FROM news
            ORDER BY id DESC
            LIMIT 3
        )   
        ORDER BY id ASC
    """)
    last3news=cursor.fetchall()
    
    new_found=False
    page=0
    news_data=[]
    while not new_found:
        page+=1
        ParsPage(page, news_data)
        for i in [2,1,0]:
            if list(last3news[i][1:4]) in news_data[-16:]:
                lastNew=last3news[i]
                new_found=True
        time.sleep(1)
        
    indx = news_data.index(list(lastNew[1:4]))    

    for new in news_data[:indx][::-1]:
        cursor.execute(
            "INSERT INTO news (title, date, link, detect_time, category) VALUES (?, ?, ?, ?, ?)",
            (new[0], new[1], new[2], datetime.now(), "Наука")
        )
        conn.commit()

conn.close()