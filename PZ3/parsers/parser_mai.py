import sqlite3
import os
import urllib3
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime


def parse():
    def GetNewCategory(link):
        url = link
        response = session.get(url, verify=False)
        if response.status_code == 200:
            html = response.text
        else:
            return 10

        soup = BeautifulSoup(html, 'html.parser')

        categories = [
            a.get_text(strip=True)
            for a in soup.select('a[href*="?section="]')
            if a.get_text(strip=True)
        ]

        for i in range(len(Mai_categories_list)):
            for new_category in categories:
                if new_category in Mai_categories_list[i]:
                    return i + 1
        return 10

    def ParsPage(page, news_data):
        url = f'https://mai.ru/press/news/?PAGEN_1={page}'
        response = session.get(url, verify=False)
        if response.status_code != 200:
            return news_data

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.find_all('article')

        for item in news_items:
            title = item.find('h5').text
            link = 'https://mai.ru/press/news/' + item.find_parent('a').get('href', '')

            date_tag = item.find('span', class_='badge')
            date = date_tag.get_text()
            if date[-2] != '2':
                date += ' 2026'
            if date[1] == ' ':
                date = '0' + date
            date = date.replace('янв', '01', 1).replace('фев', '02', 1).replace('мар', '03', 1) \
                       .replace('апр', '04', 1).replace('мая', '05', 1).replace('июн', '06', 1) \
                       .replace('июл', '07', 1).replace('авг', '08', 1).replace('сен', '09', 1) \
                       .replace('окт', '10', 1).replace('ноя', '11', 1).replace('дек', '12', 1)
            date = date.replace(' ', '.', 2)
            news_data.append([title, date, link, GetNewCategory(link)])
        return news_data

    Mai_categories_list = [
        ['Наука'],
        ['Достижения студентов', 'Образование 2.0'],
        ['Студенты'],
        ['Спорт'],
        ['Выставки', 'Творчество', 'Юбилеи и праздники'],
        ['International'],
        ['Сотрудничество'],
        ['Форумы и конференции', 'Конкурсы', 'Учеба'],
        ['Мероприятия для школьников', 'Прием гостей', 'Предуниверсарий МАИ', 'Траектория взлёта'],
    ]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_file_name = os.path.join(BASE_DIR, '..', 'news.db')

    conn = sqlite3.connect(db_file_name)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL,
        published_date TEXT NOT NULL,
        category_id INTEGER NOT NULL,
        university_id INTEGER NOT NULL,
        added_at TEXT DEFAULT (datetime('now'))
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS universities (
        university_id INTEGER NOT NULL,
        name TEXT NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_categories (
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL
    );
    ''')
    conn.commit()

    # проверка есть ли МАИ в universities, если нет — добавляем
    cursor.execute(
        "SELECT EXISTS(SELECT university_id FROM universities WHERE name = ?)",
        ("МАИ",)
    )
    mai_exists = bool(cursor.fetchone()[0])

    if not mai_exists:
        cursor.execute(
            "SELECT COALESCE(MAX(university_id), 0) + 1 FROM universities"
        )
        new_uni_id = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO universities (university_id, name) VALUES (?, ?)",
            (new_uni_id, "МАИ")
        )
        conn.commit()

    cursor.execute("SELECT university_id FROM universities WHERE name = ?", ("МАИ",))
    mai_id = cursor.fetchone()[0]

    # проверяем есть ли МАИшные новости в таблице
    cursor.execute(
        "SELECT EXISTS(SELECT 1 FROM news WHERE university_id = ?)",
        (mai_id,)
    )
    mai_news_exists = bool(cursor.fetchone()[0])

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    session.verify = False

    if not mai_news_exists:
        news_data = []
        for page in range(1, 10):
            ParsPage(page, news_data)
            time.sleep(0.1)

        for new in news_data[::-1]:
            cursor.execute(
                "INSERT OR IGNORE INTO news (title, published_date, link, category_id, university_id) VALUES (?, ?, ?, ?, ?)",
                (new[0], new[1], new[2], new[3], mai_id)
            )
            print("Новость добавлена", new[0])
        conn.commit()

    else:
        cursor.execute('''
            SELECT title, published_date, link, category_id, university_id
            FROM news
            WHERE university_id = ?
            ORDER BY id DESC
            LIMIT 3
        ''', (mai_id,))

        last3news = cursor.fetchall()

        new_found = False
        page = 0
        news_data = []
        MAX_PAGES_LOOKBACK = 15

        while not new_found and page < MAX_PAGES_LOOKBACK:
            page += 1
            before = len(news_data)
            ParsPage(page, news_data)

            if len(news_data) == before:
                print(f"[MAI] Страница {page} пуста, выходим")
                break

            new_triples = [item[:3] for item in news_data[-16:]]
            for i in [2, 1, 0]:
                if list(last3news[i][:3]) in new_triples:
                    lastNew = last3news[i]
                    new_found = True
                    break

            time.sleep(0.1)

        if new_found:
            indx = None
            for i, item in enumerate(news_data):
                if item[:3] == list(lastNew[:3]):
                    indx = i
                    break
            if indx is None:
                indx = len(news_data)

            for new in news_data[:indx][::-1]:
                cursor.execute(
                    "INSERT OR IGNORE INTO news (title, published_date, link, category_id, university_id) VALUES (?, ?, ?, ?, ?)",
                    (new[0], new[1], new[2], new[3], mai_id)
                )
                print("Новость добавлена", new[0])
            conn.commit()
        else:
            print(f"[MAI] За {MAX_PAGES_LOOKBACK} страниц совпадений не найдено, пропускаем")

    conn.close()