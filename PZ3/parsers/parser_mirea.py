from bs4 import BeautifulSoup
import requests
from datetime import datetime
import sqlite3


def connect_get_cursor(db):
    conn = None
    cursor = None
    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        print(f"[connect_get_cursor] Ошибка подключения к БД: {e}")
        if conn:
            conn.close()
        return None, None


def create_news_table(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news( 
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                published_date TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                university_id INTEGER NOT NULL,
                content TEXT,
                added_at TEXT DEFAULT (datetime('now'))
            ); 
        ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"[create_news_table] Ошибка: {e}")
        conn.rollback()


def create_categories_table(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_categories (
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL
            );
        ''')

        num = cursor.execute('''
            SELECT COUNT(*) FROM news_categories;
        ''').fetchone()

        if num[0] == 0:
            cursor.execute('''
                INSERT INTO news_categories (category_id, name) VALUES
                (1, 'Наука и инновации'),
                (2, 'Образование'),
                (3, 'Студенческая жизнь'),
                (4, 'Спорт'),
                (5, 'Культура и творчество'),
                (6, 'Международная деятельность'),
                (7, 'Сотрудничество и партнёрство'),
                (8, 'Объявления и события'),
                (9, 'Абитуриентам'),
                (10, 'Без категории')
            ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"[create_categories_table] Ошибка: {e}")
        conn.rollback()


def create_university_tables(cursor, conn):
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS universities (
                university_id INTEGER NOT NULL,
                name TEXT NOT NULL
            );
        ''')

        num = cursor.execute('''
            SELECT COUNT(*) FROM universities;
        ''').fetchone()
        if num[0] == 0:
            cursor.execute('''
                INSERT INTO universities (university_id, name) VALUES 
                (1, 'МАИ'),
                (2, 'РЭУ'),
                (3, 'МИФИ'),
                (4, 'ВШЭ'),
                (5, 'МИРЭА'),
                (6, 'КФУ')
            ''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"[create_university_tables] Ошибка: {e}")
        conn.rollback()


def get_university_id(cursor, name):
    try:
        uni_id = cursor.execute('''
            SELECT university_id FROM universities
            WHERE name = ?;
        ''', (name,)).fetchone()
        return uni_id[0] if uni_id else None
    except sqlite3.Error as e:
        print(f"[get_university_id] Ошибка: {e}")
        return None
    finally:
        pass


def get_category_id(cursor, cat):
    try:
        cat_id = cursor.execute('''
            SELECT category_id FROM news_categories
            WHERE name = ?;
        ''', (cat,)).fetchone()
        return cat_id[0] if cat_id else None
    except sqlite3.Error as e:
        print(f"[get_category_id] Ошибка: {e}")
        return None


def get_last_link(cursor):
    try:
        row = cursor.execute('''
            SELECT link FROM news n
            JOIN universities u ON u.university_id = n.university_id
            WHERE u.name = 'МИРЭА'
            ORDER BY published_date DESC
            LIMIT 1;
        ''').fetchone()

        link = row[0] if row else None
        return link
    except sqlite3.Error as e:
        print(f"[get_last_link] Ошибка: {e}")
        return None


def print_all_rows(cursor):
    try:
        cursor.execute('''
            SELECT * 
            FROM news
        ''')
        print(cursor.fetchall())
    except sqlite3.Error as e:
        print(f"[print_all_rows] Ошибка: {e}")


def insert_news(cursor, conn, title, link, dt, category_id, university_id, content):
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO news (title, link, published_date, category_id, university_id) VALUES (?, ?, ?, ?, ?);
        ''', (title, link, dt, category_id, university_id))
        conn.commit()
    except sqlite3.Error as e:
        print(f"[insert_news] Ошибка: {e}")
        conn.rollback()

def normalise_category(input_cat):
    if not input_cat:
        return "Без категории"

    key = input_cat.strip().lower()

    mapping = {
        # --- Наука и инновации ---
        "пиш": "Наука и инновации",  # передовые инженерные школы
        "иии": "Наука и инновации",  # институт ИИ
        "идеи будущего": "Наука и инновации",
        "химбиотех": "Наука и инновации",

        # --- Образование ---
        "математический праздник": "Образование",
        "яндекс лицей": "Образование",
        "мпош": "Образование",  # московская предпроф. олимпиада школьников
        "мош": "Образование",  # московская олимпиада школьников
        "омо": "Образование",  # организационно-методический отдел
        "оммо": "Образование",  # объединённая межвузовская мат. олимпиада
        "охо": "Образование",
        "всош": "Образование",  # всерос олимпиада школьников
        "вош": "Образование",  # всерос олимпиада
        "математическая вертикаль": "Образование",
        "предпрофессиональная": "Образование",
        "профориентация": "Образование",
        "многопрофильная инженерная олимпиада «звезда»": "Образование",
        "многопрофильная олимпиада рту мирэа": "Образование",
        "олимпиады": "Образование",
        "конкурсы": "Образование",
        "прикладной конкурс «золотая дюжина»": "Образование",
        "технокалейдоскоп": "Образование",
        "шаг в будущее": "Образование",
        "лига инженеров": "Образование",
        "нто": "Образование",  # нац. технологическая олимпиада

        # --- Студенческая жизнь ---
        "вектор успеха": "Студенческая жизнь",
        "математические бои": "Студенческая жизнь",
        "химические бои": "Студенческая жизнь",
        "химический праздник": "Студенческая жизнь",
        "ученик года": "Студенческая жизнь",
        "интеллектуальные игры": "Студенческая жизнь",
        "киберспорт": "Студенческая жизнь",
        "кибербиатлон": "Студенческая жизнь",
        "ит-вертикаль": "Студенческая жизнь",
        "достижения": "Студенческая жизнь",

        # --- Объявления и события ---
        "дод": "Объявления и события",  # день открытых дверей
        "дни открытых дверей": "Объявления и события",

        # --- Абитуриентам ---
        "приемная комиссия": "Абитуриентам",
        "приёмная кампания": "Абитуриентам",
        "абитуриентам": "Абитуриентам",
        "навигатор поступления": "Абитуриентам",
        "детский технопарк": "Абитуриентам",
        "фрязино": "Абитуриентам",

        # --- Сотрудничество и партнёрство ---
        "партнеры": "Сотрудничество и партнёрство",
        "сотрудничество со школами": "Сотрудничество и партнёрство",
    }

    return mapping.get(key, "Без категории")


def update_db(conn, cur, page, meta, last_link):
    response = requests.get(page, headers=meta)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')

        cards = soup.select('.article-body')

        for card in cards:
            category_block = card.select_one('ul')
            if category_block:
                categories = [cat.text.strip() for cat in category_block.select('a')]
                cat = normalise_category(categories[0]) if categories else 'Без категории'
            else:
                cat = 'Без категории'

            href_tag = card.find('a')
            href = "https://priem.mirea.ru/" + href_tag.get('href')
            if last_link != href:
                title = card.select_one('.article-header').text.strip()
                time_tag = card.find('time')
                dt_iso = time_tag.get('datetime')
                dt_with_tz = datetime.fromisoformat(dt_iso)
                dt_naive = dt_with_tz.replace(tzinfo=None)
                descript = card.select_one('.article-introtext').text.strip()
                cat_id = get_category_id(cur, cat)
                uni_id = get_university_id(cur, 'МИРЭА')
                insert_news(cur, conn, title, href, dt_naive, cat_id, uni_id, descript)
                print("Новость успешно добавлена")
            else:
                print('Не добавленных в базу новостей нет')
                return 'Completed'

    else:
        print('Ошибка на странице:', page, response.status_code)
        return False

def parse():
    connection, cursor = connect_get_cursor('news.db')
    create_news_table(cursor, connection)
    create_categories_table(cursor, connection)
    create_university_tables(cursor, connection)
    last = get_last_link(cursor)
    print('Последняя новость в базе:', last)


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'ru-RU,ru;q=0.9'
    }

    first_resp = requests.get("https://priem.mirea.ru/news?start=0")
    if first_resp:
        soup = BeautifulSoup(first_resp.text, 'html.parser')
        counter_str = soup.select_one('.com-content-category-blog__counter.counter.float-md-end.pt-3.pe-2').text
        num_of_pages = int(counter_str.split()[-1])

        for i in range(0, num_of_pages - 1):
            url = f"https://priem.mirea.ru/news?start={i * 9}"
            status = update_db(connection, cursor, url, headers, last)
            if status == 'Completed':
                break
    else:
        print(first_resp.status_code)
        return False


    print_all_rows(cursor)
    connection.close()

if __name__ == '__main__':
    parse()