# import sqlite3
# import os
# import urllib3
# import requests
# import time
# from bs4 import BeautifulSoup
# from datetime import datetime

# # # Отключаем предупреждения о небезопасном SSL
# # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# # session = requests.Session()
# # session.verify = False  # Отключаем проверку для всей сессии

# '''
# ссылки
# 1. наука и инновации 
# Наука - https://mai.ru/press/news/?tags=1235&PAGEN_1=1
# 2. образование
# Достижения студентов - https://mai.ru/press/news/?tags=9344&PAGEN_1=2
# Образование 2.0 - https://mai.ru/press/news/?tags=10312&PAGEN_1=2
# 3. Студенческая жизнь 
# Студенты - https://mai.ru/press/news/?tags=1249&PAGEN_1=2
# 4. спорт
# Спорт - https://mai.ru/press/news/?tags=1238&PAGEN_1=2
# 5. культура и творчество
# Выставки - https://mai.ru/press/news/?tags=1241&PAGEN_1=2
# Творчество - https://mai.ru/press/news/?tags=1240&PAGEN_1=2
# Юбилеи и праздники - https://mai.ru/press/news/?tags=1244&PAGEN_1=2
# 6. международная деятельность 
# Интернешнл - https://mai.ru/press/news/?tags=5203&PAGEN_1=2
# 7. сотрудничество и партнерство 
# Сотрудничество - https://mai.ru/press/news/?tags=2885&PAGEN_1=2
# 8. Объявления и события
# Форумы и конференции
# Конкурсы
# Учеба
# 9. Абитуриентам
# Мероприятия для школьников
# Прием гостей
# Предуниверсарий маи
# Траектория взлёта
# '''


# # def GetNewsCategory(link):
# #     url = link
# #     response = session.get(url, verify=False)
# #     if response.status_code==200:
# #         html = response.text

# #     soup = BeautifulSoup(html, 'html.parser')

# #     categories = [
# #         a.get_text(strip=True)
# #         for a in soup.select('a[href*="?section="]')
# #         if a.get_text(strip=True)
# #     ]

# # url = 'https://mai.ru/press/news/detail.php?ID=189467'
# # response = requests.get(url)
# # if response.status_code==200:
# #     html = response.text
# #     with open('MaiNew1.html', 'w', encoding='utf-8') as file:
# #         file.write(html)

# # with open('MaiNew1.html', 'r', encoding='utf-8') as file:
# #     content = file.read()
# #     soup = BeautifulSoup(content, 'html.parser')

# #     categories = [
# #         a.get_text(strip=True)
# #         for a in soup.select('a[href*="?section="]')
# #         if a.get_text(strip=True)
# #     ]

# #     print(categories)
        

# # ref_categories= {
# #     "Наука и инновации": ['Наука'],
# #     "Образование":['Достижения студентов','Образование 2.0'],
# #     "Студенческая жизнь":['Студенты',],
# #     "Спорт":['Спорт'],
# #     "Культура и творчество":['Выставки','Творчество','Юбилеи и праздники'],
# #     "Международная деятельность":['International'],
# #     "Сотрудничество и партнерство":['Сотрудничество'],
# #     "Объявления и события":['Форумы и конференции','Конкурсы','Учеба'],
# #     "Абитуриентам":['Мероприятия для школьников','Прием гостей','Предуниверсарий МАИ','Траектория взлёта'],
# #     }

# # for ref_category in ref_categories.items():
# #     print(ref_category, 'Наука' in ref_category[1])

# db_file_name='test3.db'

# # Подключение к файлу бд (создаётся автоматически, если не существует)
# conn = sqlite3.connect(db_file_name)
# cursor = conn.cursor()

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS universities (
#         university_id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL
#     );
# ''')
# conn.commit()

# # cursor.execute(
# #                 "INSERT INTO universities (name) VALUES (?)",
# #                 ("СПБГУ",)
# # )
# # conn.commit()
# # cursor.execute(
# #                 "INSERT INTO universities (name) VALUES (?)",
# #                 ("МИРЕА",)
# # )
# # conn.commit()
# # cursor.execute(
# #                 "INSERT INTO universities (name) VALUES (?)",
# #                 ("МИИТ",)
# # )
# # conn.commit()

# # Все строки
# cursor.execute("SELECT * FROM universities ORDER BY university_id")
# rows = cursor.fetchall()
# for row in rows:
#     print(row)


# cursor.execute(
#     "SELECT EXISTS(SELECT 1 FROM universities WHERE name = ?)",
#     ("МАИ",)
# )
# exists = bool(cursor.fetchone()[0])

# print(exists)
# conn.close()
print(10)