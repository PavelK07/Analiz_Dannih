import requests
import csv
import os
import shutil
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import urllib3

folder = "MtusiParsing2"

# Создаём сессию, чтобы сохранять настройки между запросами
session = requests.Session()
# Устанавливаем заголовки, которые имитируют работу браузера
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://mtuci.ru/',  # Иногда сайты проверяют, откуда пришли
})

# 1 часть. Запись в файлы отдельно, чтобы не делать запросы каждый раз
CreateFile=0
if CreateFile:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

    for page in range(1,5): #  5-mtusi
        url = f'https://mtuci.ru/about_the_university/news/?tags%5B0%5D=&tags%5B1%5D=76&PAGEN_1={page}'
        response = session.get(url, timeout=10)
        if response.status_code==200:
            html = response.text
            with open(os.path.join(folder, f'MtusiNews2_Page_{page}.html'), 'w', encoding='utf-8') as file:
                file.write(html)
        else: print(f'Error {response.status_code}')


# 2 часть. Чтение из файлов и работа с BeautifulSoup
CreateCSV=1
if CreateCSV:
    if os.path.exists(os.path.join(folder, 'news_Mtusi2.csv')):
        os.remove(os.path.join(folder, 'news_Mtusi2.csv'))
        
    news_data=[]

    for page in range(1,5): # 28
        with open(os.path.join(folder, f'MtusiNews2_Page_{page}.html'), 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')

            news_items = soup.select('.news-list__item')

            for item in news_items:
                title = item.find('p', class_='title').text
                print(title)

                # date_tag = item.find('span', class_='badge')
                date_tag = item.find('p', class_='meta')
                date = date_tag.get_text()
                print(date)
                break
                if date[-2]!='2':
                    date += ' 2026'
                if date[1]==' ':
                    date = '0'+ date
                
                date = date.replace('янв','01',1).replace('фев','02',1).replace('мар','03',1).replace('апр','04',1).replace('мая','05',1).replace('июн','06',1).replace('июл','07',1).replace('авг','08',1).replace('сен','09',1).replace('окт','10',1).replace('ноя','11',1).replace('дек','12',1)
                date = date.replace(' ','.',2)
                news_data.append([date, title])
                print(news_data)
                break

    # print(len(news_data))

    # with open(os.path.join(folder, 'news_Mai2.csv'), 'w', newline='', encoding='utf-8') as file:
    #     writer = csv.writer(file)
    #     for row in news_data:
    #         writer.writerow(row)

# # 3 часть. графики
# df = pd.read_csv(os.path.join(folder, 'news_Mai2.csv'), 
#                  header=None, 
#                  names=['date', 'title'], 
#                  quotechar='"', 
#                  encoding='utf-8')

# # Преобразование даты в datetime
# df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')

# df['year'] = df['date'].dt.year
# df['month'] = df['date'].dt.month

# grouped = df.groupby(['year', 'month']).size().reset_index(name='count')

# # year_month для удобного графика
# grouped['year_month'] = grouped['year'].astype(str) + '-' + grouped['month'].astype(str).str.zfill(2)

# grouped = grouped.sort_values(['year', 'month'])

# plt.figure(figsize=(12, 6))
# plt.bar(grouped['year_month'], grouped['count'], color='skyblue', edgecolor='black')
# plt.xlabel('Год-месяц')
# plt.ylabel('Количество новостей')
# plt.title('Распределение количества новостей по годам и месяцам')
# plt.xticks(rotation=45, ha='right')
# plt.tight_layout()
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.show()