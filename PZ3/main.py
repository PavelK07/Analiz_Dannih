import os
import sys
import json
import time
import sqlite3
import logging
import importlib.util
import traceback
from datetime import datetime, timedelta

DEFAULT_CONFIG = {
    "interval_minutes": 60,
    "news_db": "news.db",
    "users_db": "users.db",
    "output_file": "send_list.txt",
    "parsers_dir": "parsers"
}

CONFIG_FILE = "config.json"
LOG_FILE = "monitor.log"


def setup_logging():
    logger = logging.getLogger("monitor")
    logger.setLevel(logging.INFO)

    # Чтобы не дублировать обработчики при повторных вызовах
    if logger.handlers:
        return logger

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Консоль
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # Файл
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except OSError as e:
        logger.warning("Не удалось открыть файл лога %s: %s", LOG_FILE, e)

    return logger

log = setup_logging()


def load_config(path=CONFIG_FILE):
    # Загружает конфигурацию из JSON-файла.
    # Если файл отсутствует или повреждён — использует значения по умолчанию и создаёт файл с настройками по умолчанию.
    if not os.path.exists(path):
        log.warning("Файл конфигурации %s не найден. Создан с значениями по умолчанию.", path)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        except OSError as e:
            log.error("Не удалось создать %s: %s", path, e)
        return dict(DEFAULT_CONFIG)

    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log.error("Ошибка чтения %s: %s. Использую значения по умолчанию.", path, e)
        return dict(DEFAULT_CONFIG)

    # Дополняем отсутствующие ключи значениями по умолчанию
    for key, value in DEFAULT_CONFIG.items():
        cfg.setdefault(key, value)

    try:
        cfg["interval_minutes"] = int(cfg["interval_minutes"])
        if cfg["interval_minutes"] <= 0:
            raise ValueError
    except (ValueError, TypeError):
        log.warning("Некорректный interval_minutes, установлено 60.")
        cfg["interval_minutes"] = 60

    return cfg


def ensure_news_schema(conn):
    # Создаёт таблицы новостей, категорий и вузов, если их нет.
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published_date TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            university_id INTEGER NOT NULL,
            added_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS news_categories (
            category_id INTEGER NOT NULL,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS universities (
            university_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    """)
    conn.commit()


def ensure_users_schema(conn):
    # Создаёт таблицы пользователей и их категорий, если их нет.
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS user_categories (
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()


def open_news_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    ensure_news_schema(conn)
    return conn


def open_users_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    ensure_users_schema(conn)
    return conn


def load_parsers(parsers_dir):
    parsers = []

    if not os.path.isdir(parsers_dir):
        log.error("Папка парсеров '%s' не найдена.", parsers_dir)
        return parsers

    for filename in sorted(os.listdir(parsers_dir)):
        if not filename.endswith(".py"):
            continue
        if not filename.startswith("parser_"):
            continue
        if filename.startswith("__"):
            continue

        module_name = filename[:-3]
        filepath = os.path.join(parsers_dir, filename)

        try:
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                log.error("Не удалось создать spec для %s", filepath)
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            parse_func = getattr(module, "parse", None)
            if not callable(parse_func):
                log.warning("В модуле %s отсутствует функция parse(). Пропуск.", module_name)
                continue

            parsers.append((module_name, parse_func))
            log.info("Загружен парсер: %s", module_name)

        except Exception as e:
            log.error("Ошибка загрузки парсера %s: %s", module_name, e)
            log.debug(traceback.format_exc())

    return parsers


def run_parsers(parsers):
    log.info("=== Запуск парсеров (%d шт.) ===", len(parsers))
    for name, parse_func in parsers:
        try:
            log.info("Запуск %s...", name)
            parse_func()
            log.info("%s завершён успешно.", name)
        except Exception as e:
            # Парсер не должен «ронять» планировщик
            log.error("Ошибка в парсере %s: %s", name, e)
            log.debug(traceback.format_exc())
    log.info("=== Все парсеры завершены ===")


# ----------------------------- Анализ новостей и пользователей -----------------------------

def fetch_new_news(news_conn, since_iso):
    """
    Возвращает список новых новостей, добавленных после since_iso
    (сравнение по added_at). Каждая запись — sqlite3.Row.
    """
    cur = news_conn.cursor()
    cur.execute("""
        SELECT id, title, link, published_date, category_id, university_id, added_at
        FROM news
        WHERE added_at > ?
        ORDER BY added_at ASC, id ASC
    """, (since_iso,))
    return cur.fetchall()


def fetch_users_with_categories(users_conn):
    cur = users_conn.cursor()
    cur.execute("SELECT id, name, email FROM users")
    users = {row["id"]: {"name": row["name"],
                         "email": row["email"],
                         "categories": set()} for row in cur.fetchall()}

    cur.execute("SELECT user_id, category_id FROM user_categories")
    for row in cur.fetchall():
        uid = row["user_id"]
        if uid in users:
            users[uid]["categories"].add(row["category_id"])

    return users


def build_send_list(news_rows, users):
    result = {uid: [] for uid in users}

    for news in news_rows:
        cat = news["category_id"]
        nid = news["id"]
        for uid, info in users.items():
            if cat in info["categories"]:
                result[uid].append(nid)

    return result


def write_send_list(path, send_map, users):
    try:
        with open(path, "w", encoding="utf-8") as f:
            for uid, news_ids in send_map.items():
                if not news_ids:
                    continue
                line = "{}: {}".format(uid, ", ".join(str(n) for n in news_ids))
                f.write(line + "\n")
        log.info("Файл рассылки записан: %s", path)
    except OSError as e:
        log.error("Не удалось записать %s: %s", path, e)


def run_cycle(parsers, cfg, last_run_iso):
    # Фиксируем время начала цикла ДО парсинга —
    # чтобы на следующем шаге забрать всё, что добавилось после.
    cycle_start = datetime.now()
    cycle_start_iso = cycle_start.strftime("%Y-%m-%d %H:%M:%S")

    log.info("----- Новый цикл, начало: %s -----", cycle_start_iso)

    # 1. Парсеры
    run_parsers(parsers)

    # 2. Открываем БД
    try:
        news_conn = open_news_db(cfg["news_db"])
    except sqlite3.Error as e:
        log.error("Не удалось открыть %s: %s", cfg["news_db"], e)
        return last_run_iso

    try:
        users_conn = open_users_db(cfg["users_db"])
    except sqlite3.Error as e:
        log.error("Не удалось открыть %s: %s", cfg["users_db"], e)
        news_conn.close()
        return last_run_iso

    try:
        # 3. Новые новости за интервал
        new_news = fetch_new_news(news_conn, last_run_iso)
        log.info("Новых новостей за интервал: %d", len(new_news))

        # 4. Пользователи и их категории
        users = fetch_users_with_categories(users_conn)
        log.info("Пользователей в БД: %d", len(users))

        # 5. Формируем рассылку
        send_map = build_send_list(new_news, users)

        total_links = sum(len(v) for v in send_map.values())
        log.info("Всего связей пользователь-новость: %d", total_links)

        # 6. Пишем файл
        write_send_list(cfg["output_file"], send_map, users)

    except sqlite3.Error as e:
        log.error("Ошибка БД во время анализа: %s", e)
    finally:
        news_conn.close()
        users_conn.close()

    log.info("----- Цикл завершён -----")
    return cycle_start_iso


def main():
    log.info("========================================")
    log.info("Мониторинговый сервис новостей вузов")
    log.info("Запуск: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("========================================")

    cfg = load_config()
    log.info("Конфигурация: %s", json.dumps(cfg, ensure_ascii=False))

    parsers = load_parsers(cfg["parsers_dir"])
    if not parsers:
        log.warning("Не найдено ни одного парсера в '%s'.", cfg["parsers_dir"])

    interval_sec = cfg["interval_minutes"] * 60

    # Инициализируем время последнего запуска: считаем, что до старта
    # ничего не обрабатывали — берём «очень давнее» время, чтобы
    # первый цикл увидел все новости в БД.
    last_run_iso = "1970-01-01 00:00:00"

    try:
        while True:
            last_run_iso = run_cycle(parsers, cfg, last_run_iso)

            log.info("Следующий запуск через %d мин.", cfg["interval_minutes"])
            time.sleep(interval_sec)

    except KeyboardInterrupt:
        log.info("Получен Ctrl+C. Завершение работы.")
    except Exception as e:
        log.error("Непредвиденная ошибка: %s", e)
        log.debug(traceback.format_exc())
    finally:
        log.info("Программа остановлена.")
        logging.shutdown()


if __name__ == "__main__":
    main()