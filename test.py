# # import requests
# # import csv
# # import os
# # import shutil


# # a='9 июн 2025'
# # a=a.replace('июн','06',1)
# # print(a, int('06'))


# # # dates=[]
# # # with open(os.path.join(folder, 'news_Mai2.csv'), 'r', encoding='utf-8') as file:
# # #     reader = csv.reader(file)
# # #     for row in reader:
# # #         print(row[0][3:5],row[0][6:10])

a=[1.2,3,4,5,6]
print(a[::-1])



# import sqlite3
# import os
# import urllib3
# import requests
# from bs4 import BeautifulSoup
# from datetime import datetime
# # Отключаем предупреждения о небезопасном SSL
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# session = requests.Session()
# session.verify = False  # Отключаем проверку для всей сессии


# news_data=[]
# for page in range(1,2):
#         url = f'https://mai.ru/press/news/?tags=1235&PAGEN_1={page}'
#         response = session.get(url, verify=False)
#         if response.status_code==200:
#             html = response.text

#         soup = BeautifulSoup(html, 'html.parser')

#         news_items = soup.find_all('article')
    
#         for item in news_items:
#             title = item.find('h5').text  

#             # link_tag = item.find_parent('a')
#             # if link_tag:
#             #     link = link_tag.get('href', '')
#             #     if link and not link.startswith('http'):
#             #         link = 'https://mai.ru/press/news/' + link
            
#             link = 'https://mai.ru/press/news/' + item.find_parent('a').get('href', '')
#             print(link)

#             # date_tag = item.find('span', class_='badge')
#             # date = date_tag.get_text()
#             # if date[-2]!='2':
#             #     date += ' 2026'
#             # if date[1]==' ':
#             #     date = '0'+ date
            
#             # date = date.replace('янв','01',1).replace('фев','02',1).replace('мар','03',1).replace('апр','04',1).replace('мая','05',1).replace('июн','06',1).replace('июл','07',1).replace('авг','08',1).replace('сен','09',1).replace('окт','10',1).replace('ноя','11',1).replace('дек','12',1)
#             # date = date.replace(' ','.',2)
#             # news_data.append([date, title])








