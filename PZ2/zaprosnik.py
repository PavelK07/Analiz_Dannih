import sqlite3
import os
import urllib3
import requests
from bs4 import BeautifulSoup
from datetime import datetime


db_file_name='news_mai.db'

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

# Все строки
cursor.execute("SELECT * FROM news ORDER BY id DESC LIMIT 30")
rows = cursor.fetchall()
for row in rows:
    print(row)


conn.close()
