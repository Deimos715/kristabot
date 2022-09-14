import sqlite3
import datetime


# Создание БД
def create_table_ros():
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()

        # Создание таблицы
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS ROS(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        publication TEXT,
        pdf_link TEXT,
        parsing_date DATE
        );''')
        db.commit()


def insert_ros(col1, col2, col3):
    # Вставка в таблицу БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        data_list = (col1, col2, col3, datetime.datetime.now())
        cursor.execute('''
                        INSERT INTO ros (title, publication, pdf_link, parsing_date)
                        VALUES (?, ?, ?, ?);
                            ''', data_list)
        db.commit()


def check_ros(title):
    # Проверка записи на наличие в базе
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT title FROM ros WHERE title = ? ''', (title,))
        result = cursor.fetchall()
        if len(result) == 0:
            print('[INFO] Такой записи нет')
            return 0
        else:
            print('[X] Такая запись существует')
            return 1


def get_data_from_db_ros():
    # Получение данных из БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT title, publication, pdf_link FROM ros''')
        # Вывод всех документов
        data_set = cursor.fetchall()
        return data_set


# Создание БД
def create_table_min():
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()

        # Создание таблицы
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MINFIN(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_doc TEXT
        tag TEXT,
        date_doc TEXT,
        type_doc TEXT,
        title_doc TEXT,
        file_info_doc TEXT,
        reg TEXT,
        link_download TEXT,
        parsing_date DATE
        );''')
        db.commit()


def insert_min(col1, col2, col3, col4, col5, col6, col7, col8):
    # Вставка в таблицу БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        data_list = (col1, col2, col3, col4, str(col5), str(col6), col7, str(col8), datetime.datetime.now())
        cursor.execute('''
                        INSERT INTO minfin (link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg, 
                        link_download, parsing_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            ''', data_list)
        db.commit()


def check_min(link_doc):
    # Проверка записи на наличие в базе
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT link_doc FROM minfin WHERE link_doc = ? ''', (link_doc,))
        result = cursor.fetchall()
        if len(result) == 0:
            print('[INFO] Такой записи нет')
            return 0
        else:
            print('[X] Такая запись существует')
            return 1


def get_data_from_db_min():
    # Получение данных из БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg, link_download FROM 
        minfin''')
        # Вывод всех документов
        data_set = cursor.fetchall()
        return data_set
