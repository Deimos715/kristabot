import sqlite3
import datetime


# Создание БД Ros
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




# Создание БД Minfin
def create_table_min():
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()

        # Создание таблицы
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS MINFIN(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link_doc TEXT,
        tag TEXT,
        date_doc TEXT,
        type_doc TEXT,
        title_doc TEXT,
        file_info_doc TEXT,
        reg TEXT,
        link_download TEXT,
        date_update TEXT,
        parsing_date DATE
        );''')
        db.commit()


def insert_min(col1, col2, col3, col4, col5, col6, col7, col8, col9):
    # Вставка в таблицу БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        data_list = (col1, col2, col3, col4, str(col5), str(col6), col7, str(col8), str(col9), datetime.datetime.now())
        cursor.execute('''
                        INSERT INTO minfin (link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg, 
                        link_download, date_update, parsing_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                            ''', data_list)
        db.commit()


def check_min(title_doc, date_update):
    # Проверка записи на наличие в базе
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''
            SELECT id FROM minfin WHERE title_doc = ? AND date_update = ? ''', (title_doc, date_update))
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
        cursor.execute('''SELECT link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg, link_download, date_update FROM 
        minfin''')
        # Вывод всех документов
        data_set = cursor.fetchall()
        return data_set




# Создание БД Publication_gov
def create_table_govp():
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()

        # Создание таблицы
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS GOVP(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        view_date TEXT,
        complex_name TEXT,
        document_date TEXT,
        reg_number TEXT,
        document_date_reg TEXT,
        pages_count TEXT,
        eo_number TEXT,
        link_doc TEXT,
        parsing_date DATE
        );''')
        db.commit()


def insert_govp(col1, col2, col3, col4, col5, col6, col7, col8):
    # Вставка в таблицу БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        data_list = (col1, col2, col3, col4, col5, col6, col7, col8, datetime.datetime.now())
        cursor.execute('''
                        INSERT INTO govp (view_date, complex_name, document_date, reg_number, document_date_reg, pages_count, eo_number, link_doc, parsing_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                            ''', data_list)
        db.commit()


def check_govp(complex_name):
    # Проверка записи на наличие в базе
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT complex_name FROM govp WHERE complex_name = ? ''', (complex_name,))
        result = cursor.fetchall()
        if len(result) == 0:
            print('[INFO] Такой записи нет')
            return 0
        else:
            print('[X] Такая запись существует')
            return 1


def get_data_from_db_govp():
    # Получение данных из БД
    with sqlite3.connect('bot_bd.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT view_date, complex_name, document_date, reg_number, document_date_reg, pages_count, eo_number, link_doc FROM 
        govp''')
        # Вывод всех документов
        data_set = cursor.fetchall()
        return data_set