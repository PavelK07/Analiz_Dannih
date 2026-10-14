import requests
import csv
import os
import shutil
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import urllib3
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

folder = "MaiParsing2"

# Отключаем предупреждения о небезопасном SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = False  # Отключаем проверку для всей сессии

# 1 часть. Запись в файлы отдельно, чтобы не делать запросы каждый раз
CreateFile=1
if CreateFile:
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)

    for page in range(1,6):
        url = f'https://mai.ru/press/news/?tags=1233&PAGEN_1={page}'
        response = session.get(url, verify=False)
        if response.status_code==200:
            html = response.text
            with open(os.path.join(folder, f'MaiNews2_Page_{page}.html'), 'w', encoding='utf-8') as file:
                file.write(html)
        else: print(f'Error {response.status_code}')


# 2 часть. Чтение из файлов и работа с BeautifulSoup
CreateCSV=1
if CreateCSV:
    if os.path.exists(os.path.join(folder, 'news_Mai2.csv')):
        os.remove(os.path.join(folder, 'news_Mai2.csv'))
        
    news_data=[]

    for page in range(1,6):
        with open(os.path.join(folder, f'MaiNews2_Page_{page}.html'), 'r', encoding='utf-8') as file:
            content = file.read()
            soup = BeautifulSoup(content, 'html.parser')

            news_items = soup.find_all('article')
            

            for item in news_items:
                title = item.find('h5').text  

                date_tag = item.find('span', class_='badge')
                date = date_tag.get_text()
                if date[-2]!='2':
                    date += ' 2026'
                if date[1]==' ':
                    date = '0'+ date
                
                date = date.replace('янв','01',1).replace('фев','02',1).replace('мар','03',1).replace('апр','04',1).replace('мая','05',1).replace('июн','06',1).replace('июл','07',1).replace('авг','08',1).replace('сен','09',1).replace('окт','10',1).replace('ноя','11',1).replace('дек','12',1)
                date = date.replace(' ','.',2)
                news_data.append([date, title])

    print(len(news_data))

    with open(os.path.join(folder, 'news_Mai2.csv'), 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in news_data:
            writer.writerow(row)

# 3 часть. графики
df = pd.read_csv(os.path.join(folder, 'news_Mai2.csv'),
                 header=None,
                 names=['date', 'title'],
                 quotechar='"',
                 encoding='utf-8')

df['date'] = pd.to_datetime(df['date'], format='%d.%m.%Y')

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

grouped = df.groupby(['year', 'month']).size().reset_index(name='count')
grouped['year_month'] = grouped['year'].astype(str) + '-' + grouped['month'].astype(str).str.zfill(2)
grouped = grouped.sort_values(['year', 'month'])

plt.figure(figsize=(12, 6))
plt.bar(grouped['year_month'], grouped['count'], color='skyblue', edgecolor='black')
plt.xlabel('Год-месяц')
plt.ylabel('Количество новостей')
plt.title('Распределение количества новостей по годам и месяцам')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig(os.path.join(folder, 'chart_year_month.png'), dpi=150)
plt.show()
plt.close()

# Дополнительный график только по месяцам, суммарно за все года
monthly = df.groupby('month').size().reset_index(name='count')
month_names = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
               'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
monthly['month_name'] = monthly['month'].apply(lambda m: month_names[m - 1])

# 4 часть. DOCX-отчёт
doc = Document()

title_paragraph = doc.add_heading('Отчёт по новостям МАИ', level=0)
title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_paragraph(f'Дата создания отчёта: {datetime.now().strftime("%d.%m.%Y %H:%M")}')
doc.add_paragraph(f'Всего публикаций: {len(df)}')
doc.add_paragraph(f'Период: с {df["date"].min().strftime("%d.%m.%Y")} по {df["date"].max().strftime("%d.%m.%Y")}')

# Раздел с графиком по годам/месяцам
doc.add_heading('Распределение по годам и месяцам', level=1)
doc.add_picture(os.path.join(folder, 'chart_year_month.png'), width=Inches(6.5))
last_paragraph = doc.paragraphs[-1]
last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Раздел с таблицей публикаций
doc.add_heading('Таблица публикаций', level=1)
doc.add_paragraph(f'Всего записей в таблице: {len(df)}')

table = doc.add_table(rows=1, cols=3)
table.style = 'Light Grid Accent 1'

hdr_cells = table.rows[0].cells
hdr_cells[0].text = '№'
hdr_cells[1].text = 'Дата'
hdr_cells[2].text = 'Заголовок'

df_sorted = df.sort_values('date', ascending=False).reset_index(drop=True)

for i, row in df_sorted.iterrows():
    row_cells = table.add_row().cells
    row_cells[0].text = str(i + 1)
    row_cells[1].text = row['date'].strftime('%d.%m.%Y')
    row_cells[2].text = str(row['title'])

# Сохранение отчёта
docx_path = os.path.join(folder, 'Mai_news.docx')
doc.save(docx_path)
print(f'DOCX-отчёт сохранён: {docx_path}')