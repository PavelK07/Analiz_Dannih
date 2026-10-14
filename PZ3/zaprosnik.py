import sqlite3
import os
import urllib3
import requests
from bs4 import BeautifulSoup
from datetime import datetime


db_file_name='test3.db'

# Подключение к файлу бд (создаётся автоматически, если не существует)
conn = sqlite3.connect(db_file_name) # news_mai.db
cursor = conn.cursor()


# cursor.execute('''
#     DELETE FROM news
#     WHERE id IN (
#         SELECT id FROM news ORDER BY id DESC LIMIT 3
#     )
# ''')
# conn.commit()

# cursor.execute(
#     "INSERT INTO news (title, published_date, link, category, university) VALUES (?, ?, ?, ?, ?)",
#     ("test2", "07.06.2026", "https://test2.ru", "Наука", "МАИ")
# )
# conn.commit()

# Все строки
cursor.execute("SELECT * FROM news ORDER BY id DESC LIMIT 30")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.execute("""
    SELECT * FROM (
        SELECT * FROM news
        ORDER BY id DESC
        LIMIT 3
    )
    ORDER BY id ASC
""")
last3news=cursor.fetchall()
print(last3news)
for i in range(3):
    print(lastNew=last3news[i])

conn.close()
