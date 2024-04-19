import psycopg2
from psycopg2 import Error
try:
    connection = psycopg2.connect(user="user_name",
                                  password="password",
                                  host="ip",
                                  port="port",
                                  database="bd_name")
    cursor = connection.cursor()
    # create_table_query = '''CREATE TABLE test
    #                       (ID SERIAL PRIMARY KEY NOT NULL,
    #                       SKU           TEXT    NOT NULL,
    #                       NAME         TEXT,
    #                       PRICE int,
    #                       CATEGORY TEXT); '''
    # cursor.execute(create_table_query)
    # data_dict = {'SKU': 31890398, 'name': 'МАРКЕР', 'price': 240,
    #              'categories': [{'id_category': 5486, 'name_category': 'Канцтовары'},
    #                             {'id_category': 17159, 'name_category': 'Письменные принадлежности'}]}
    cursor = connection.cursor()
    # Выполнение SQL-запроса для вставки данных в таблицу
    insert_query = f""" INSERT INTO test (SKU, name, price, category) VALUES ('123456789', 'Тест', '999', 'Тестирование')"""
    cursor.execute(insert_query)
    connection.commit()
    print("1 запись успешно вставлена")
    # connection.commit()
    # print("Таблица успешно создана в PostgreSQL")
except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
