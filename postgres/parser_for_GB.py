import datetime
from multiprocessing import Pool
import requests
import psycopg2

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "cross-site"
}


def get_id_fitrs_good_for_search(query):
    """получение 1 товара в поисковой выдачи по ключевому словосочетанию"""
    url = f'https://search.wb.ru/exactmatch/ru/common/v4/search?TestGroup=rec_search_goods_new_model&TestID=370&appType=1&curr=rub&dest=-446087&query={query}&resultset=catalog&sort=popular&spp=26&suppressSpellcheck=false&uclusters=0'
    r = requests.get(url=url, headers=headers)
    try:
        id_first_good = r.json().get('data').get('products')[0].get('id')
    except IndexError:
        id_first_good = 0
        print(f'НЕТ РЕЗУЛЬТАТОВ ПОИСКА по запросу: "{query}"')
    except AttributeError:
        id_first_good = 0
    return id_first_good


def get_SKU_info(SKU):
    """получение названия, цены, id категории, id бренда и kind товара"""
    url = f'https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-446087&spp=26&nm={SKU}'
    r = requests.get(url=url, headers=headers)
    try:
        name = r.json().get('data').get('products')[0].get('name')
        price = (r.json().get('data').get('products')[0].get('salePriceU')) / 100
        kind = r.json().get('data').get('products')[0].get('kindId')
        brandId = r.json().get('data').get('products')[0].get('brandId')
        subjectId = r.json().get('data').get('products')[0].get('subjectId')
    except:
        name = ''
        price = 0
        kind = ''
        brandId = ''
        subjectId = ''
    return {'name': name, 'price': int(price), 'kind': kind, 'brandId': brandId, 'subjectId': subjectId}


def get_category(SKU, subjectId, kind, brandId):
    url = f'https://www.wildberries.ru/webapi/product/{SKU}/data?subject={subjectId}&kind={kind}&brand={brandId}'
    r = requests.get(url=url, headers=headers)
    paths = r.json().get('value').get('data').get('sitePath')
    categories_list = []
    try:
        for path in paths:
            categories_list.append({'id_category': path.get('id', 0), 'name_category': path.get('name', None)})
    except TypeError:
        categories_list = []
    return categories_list


def get_categories_good(article):
    try:
        vol = int(str(article)[:len(str(article)) - 5])
        part = str(article)[:len(str(article)) - 3]
        if 0 <= vol <= 143:
            number_basket = '01'
        elif 144 <= vol <= 287:
            number_basket = '02'
        elif 288 <= vol <= 431:
            number_basket = '03'
        elif 432 <= vol <= 719:
            number_basket = '04'
        elif 720 <= vol <= 1007:
            number_basket = '05'
        elif 1008 <= vol <= 1061:
            number_basket = '06'
        elif 1062 <= vol <= 1115:
            number_basket = '07'
        elif 1116 <= vol <= 1169:
            number_basket = '08'
        elif 1170 <= vol <= 1313:
            number_basket = '09'
        elif 1314 <= vol <= 1601:
            number_basket = '10'
        elif 1602 <= vol <= 1655:
            number_basket = '11'
        elif 1656 <= vol <= 1919:
            number_basket = '12'
        else:
            number_basket = '13'
        url = f'https://basket-{number_basket}.wb.ru/vol{vol}/part{part}/{article}/info/ru/card.json'
        data = requests.get(url=url).json()
        return {'subj_name': data.get('subj_name'), 'subj_root_name': data.get('subj_root_name')}
    except ValueError:
        return {}

def parser(query):
    SKU = get_id_fitrs_good_for_search(query=list(query)[1])
    good_info = get_SKU_info(SKU)
    id = list(query)[0]
    # categories = get_category(SKU=SKU,
    #                           subjectId=good_info['subjectId'],
    #                           kind=good_info['kind'],
    #                           brandId=good_info['brandId']
    #                           )
    categories = get_categories_good(SKU)
    insert_query_to_db(id, SKU, good_info['name'], good_info['price'], categories)


def insert_query_to_db(id, SKU, name, price, categories):
    # try:
    # Подключение к существующей базе данных
    # connection = psycopg2.connect(user="postgres",
    #                               # пароль, который указали при установке PostgreSQL
    #                               password="my_password",
    #                               host="127.0.0.1",
    #                               port="5432",
    #                               database="new")
    connection = conn_db()
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM wb_item WHERE id = '{id}';")
    data = cursor.fetchone()
    # if data is None:
    # if SKU == 0:
    #     pass
    # else:
    #     try:
    #         insert_query = f""" INSERT INTO wb (SKU, name, price, CATEGORY, sub_category) VALUES ('{SKU}', '{name}', '{price}', '{str(CATEGORY[0]['id_category'])}', '{str(CATEGORY[1]['id_category'])}')"""
    #     except IndexError:
    #         insert_query = f""" INSERT INTO wb (SKU, name, price, CATEGORY, sub_category) VALUES ('{SKU}', '{name}', '{price}', '{str(CATEGORY)}', '{str(CATEGORY)}')"""
    #     cursor.execute(insert_query)
    #     connection.commit()
    #     print(f"{SKU} |запись успешно вставлена")
    # else:
    # print(f'{CATEGORY}')
    # try:
    #     CATEGORY[0]["id_category"]
    # except:
    #     print(f'error {categories}')
    # try:
    #     category_one = str(categories[-2]['name_category'])
    # except IndexError:
    #     category_one = None
    # try:
    #     category_two = str(categories[-3]['name_category'])
    # except IndexError:
    #     category_two = None
    # category_one = categories.get()
    if data:
        insert_query = f"""
        UPDATE wb_item
        set price ='{price}',
        id_product = '{SKU}',
        name_product = '{name.replace("'", "")}',
        one_category = '{categories.get("subj_name")}',
        two_category = '{categories.get("subj_root_name")}' 
        where id = '{id}';
        """
        cursor.execute(insert_query)
        connection.commit()
        print(f"[!] Запись c id - {id} успешно обновлена")
    # except (Exception, Error) as error:
    #     print("Ошибка при работе с PostgreSQL", error)


# data_list = ['Простыня 200x90, спанбонд ламин., 10шт/уп, штучно, 02-197',
# 'Простыня 200x140, спанбонд ламин., 10шт/уп, штучно, 02-195',
# 'Халат хирург. н/с ЕВРО, дл.140 см, пл.42 р.52-54 5шт/уп.',
# 'Салфетка (коврик) гигиен, 40x50, спандбонд пл.30 голубой 100 шт/уп',
# 'Салфетка гигиен, 40x50, спандбонд пл.30 бордо 100 шт/уп',
# 'Накидка -Пеньюар на резинке по дек. спандбонд белый 140х75см 01-656 10шт/уп',
# 'Салфетка (коврик) гигиен, 40x50, спандбонд пл.30 белый 100 шт/уп',
# 'Коврик (салфетка) гигиен, 40x50, спандбонд пл.30 оранжевый 100 шт/уп',
# 'Салфетка (коврик), 40x50, спандбонд пл.30 сиреневый 100 шт/уп',
# 'Жгут взрослый многораз. 40х2,5 см Improvacuter',
# 'Салфетка - рулон с перфор. 70х80см, спандбонд, н/с, пл.20, 250 шт/рул',
# 'Салфетка гигиен, 40х30, спанлейс с отверст (50шт/уп)',
# 'Простыня стер. 200x80 спанлейс пл. 40-42',
# 'Трусы женские спанлейс 56-58 10шт/уп.',
# 'Трусы бикини женские, оранж, спанбонд шт/слож 25шт/уп',
# 'Накидка-Пелерина на завязках спандбонд 70х70 см 25 шт/уп',
# 'Салфетка спиртовая,антисептическая,этил.сп.60х100мм White Whale 20 шт/уп',
# 'Простыня 80х70, влагонепрон., пл. 65, Tutami papyr 20шт/уп',
# 'Мед.однораз. белье КБО - 01 (общехирургический)',
# 'Пододеяльник медицинский н/с пл.25 5шт/уп П-25 210x140см',
# 'Защитное стекло Xiaomi Redmi 9A/9C, FS FG, Red Line, чер, УТ000021561',
# 'Коврик спанбонд 80 г/кв.м 45х60 см 100 шт./уп (00-256)',
# 'Простыня н/с 70 х 80, СМС голубой, EL-P78 , 50 шт/уп',
# 'Простыня н/с 200 х 70, СМС голубой, EL-P27 , 20 шт/уп',
# 'Простыня рулонная с перф. 200 х 80, СМС 15г/м2 белый, EL-P28R, 100 шт/рул',
# 'Накидка - пеньюар п/э прозрачный 140х100 см 50 шт/уп',
# 'Простыня н/с 70 х 80, СМС голубой, SL-P78 , 50 шт/уп',
# 'Салфетка н/с 30х40см спанлейс 40 г/м2 100шт/рул.',
# 'Простыня стерил. с круг.отверст. лип.край 90х75, спанб. лам., пл.40',
# 'Простыня 200x200, полиэтилен, 25шт/уп, 00-140',
# 'Простыня 200x160, полиэтилен, 25шт/уп, 00-139',
# 'Салфетка спиртовая, антисептическая, этил. сп. 30х65мм SOYUZ 100шт/уп',
# 'Нарукавники ПНД синие 40 х 20 см 100 шт/уп',
# 'Простыня в рулоне 200x80, белый, Комфорт, 75 шт/рул, 600-492',
# 'Салфетка Полотенце однораз., Люкс спанлейс, 45x90, белый 50 шт/уп, штучно',
# 'Простыня н/с бум.ламинир.140х80 10 шт/уп,индив.сложение',
# 'Салфетка спанлейс н/с 10х10см белая 40г/м2 100 шт. 00-143',
# 'Игрушка набивная Гномик, L18 W13 H66 см, 2в. 724012',
# 'Костюм мед. хирургич.н/с (рубаш.,брюки), спанбонд, пл.42,синий р.56-58',
# 'Пакет с замком (Zip Lock) 8 х 12 см, 60 мкм, вишневый,  100 шт/уп'
# ]
# query = 'Кофе Lavazza Rossa в зернах, 1 кг'
# parser(query)
def conn_db():
    con = psycopg2.connect(
        database="name_db",
        user="user_name",
        password="password",
        host="ip",
        port="port"
    )
    return con


if __name__ == '__main__':
    start = datetime.datetime.now()  # запишем время старта
    cursor = conn_db().cursor()
    cursor.execute("""SELECT id, name FROM wb_item;""")
    data_list = cursor.fetchall()

    with Pool(30) as p:  # для увеличения скорости ставим цифру больше )))
        p.map(parser, data_list)
        # p.map(parser, data_list[1000:2000])  # можно частями, от 1000 до 2000 записи как пример

    end = datetime.datetime.now()  # запишем время завершения кода
    total = end - start  # расчитаем время затраченное на выполнение кода
    print("Затраченное время:" + str(total))
