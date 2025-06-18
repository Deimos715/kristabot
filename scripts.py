import os
import requests
import telebot
from bs4 import BeautifulSoup
import my_bd_command
import time
import datetime
from random import uniform
from chats import send_message_to_all_chats
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('token'))


# parser_minfin(приказы)
def get_html_min_b(url, params=None):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) (KHTML, like Gecko) Chrome/87.0.4280.66'}
    response = requests.get(url, headers=headers, params=params, verify=False)
    html = response.text
    return html


def get_pages_count_min_b(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        pagination = soup.find('a', class_='button_more').get("data-page-count")
        send_message_to_all_chats(bot, 'Всего страниц: ' + pagination)
        return int(pagination)-749620842
    except Exception:
        send_message_to_all_chats(bot, 'Количество страниц не найдено')


def get_content_min_b(html):
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', class_=['document_card inner_link', 'document_card inner_link important'])
    data = []
    my_bd_command.create_table_min()
    for block in blocks:
        try:
            link_doc = 'https://minfin.gov.ru' + block.get('data-href')
        except:
            link_doc = 'Ссылка на документ не найдена'

        try:
            tag = block.find('ul', class_='tag_list').get_text(strip=True)
        except:
            tag = 'Тег не найден'

        try:
            date_doc = block.find('span', class_='date').get_text(strip=True)
        except:
            date_doc = 'Дата опубликования не найдена'

        try:
            type_doc = block.find('a', class_='document_type').get_text(strip=True)
        except:
            type_doc = 'Тип документа не найден'

        try:
            title_doc = block.find('a', class_='document_title').get_text(strip=True) # Берем берем для проверки записей в БД
        except:
            title_doc = 'Заголовок документа не найден'

        try:
            file_info_doc = 'https://minfin.gov.ru' + block.find('a', class_='download_btn').get(
                'href')
        except:
            file_info_doc = 'Ссылка на файл не найдена'

        """Далее проваливаемся в ссылку карточки и берем оттуда ссылку на файл и данные о регистрации"""
        sub_page_soup = BeautifulSoup(get_html_min_b(link_doc), 'html.parser')
        try:
            reg = sub_page_soup.find('div', class_='page_description').get_text(strip=True)
        except:
            reg = 'Регистрационная информация не найдена'
        try:
            link_download = 'https://minfin.gov.ru' + sub_page_soup.find('a', class_='download_btn').get('href')
        except:
            link_download = 'Доп. ссылка на файл не найдена'
        try:
            info_block = sub_page_soup.find('div', class_='document_data_information')
            spans = info_block.find_all('span', class_='t_mn2') if info_block else []
            date_update = spans[1].get_text(strip=True) if len(spans) >= 2 else 'Дата обновления не найдена' # берем срез второго класса
        except:
            date_update = 'Дата обновления не найдена'

        try:
            if my_bd_command.check_min(title_doc, date_update) == 0:
                my_bd_command.insert_min(link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg,
                                        link_download, date_update)
                data.append({
                    'Ссылка на документ': link_doc,
                    'Тег': tag,
                    'Дата опубликования': date_doc,
                    'Тип документа': type_doc,
                    'Заголовок документа': title_doc,
                    'Ссылка на файл': file_info_doc,
                    # Детализация документа
                    'Дата обновления': date_update,
                    'Зарегистрирован': reg,
                    'Доп. ссылка на файл:': link_download
                })
                send_message_to_all_chats(bot,
                                f'Свойство: {tag}\n'
                                f'Заголовок: {title_doc}\n'
                                f'Тип документа: {type_doc}\n'
                                f'Дата публикации: {date_doc.replace("Опубликовано: ", "")}\n'
                                f'Дата изменения: {date_update.replace("Изменено: ", "")}\n'
                                f'Регистрационная информация: {reg}\n'
                                f'Ссылка: {link_doc}\n'
                                f'Ссылка на файл: {file_info_doc}\n'
                                f'Доп. ссылка на файл: {link_download}\n')
                send_message_to_all_chats(bot, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            send_message_to_all_chats(bot, '[X] Ошибка вставки данных в БД', ex)
            continue
    send_message_to_all_chats(bot, 'Количество новых документов: ' + str(len(data)))
    return data


def parser_min_b(url):
    pages = get_pages_count_min_b(get_html_min_b(url))
    data = []
    pages = 2  # берем для примера только 2 страницы
    for page in range(1, pages + 1):
        send_message_to_all_chats(bot, f'Сбор со страницы {page}')
        while True:
            try:
                data.extend(get_content_min_b(get_html_min_b(url, params={'page_65': page})))
                time.sleep(1)
                break
            except:
                send_message_to_all_chats(bot, 'Доступ прерван, ждем 5 сек.')
                for sec in range(1, 5):
                    time.sleep(1)
                    send_message_to_all_chats(bot, f'{sec}...')
                send_message_to_all_chats(bot, 'перезапуск')
    send_message_to_all_chats(bot, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


# parser_minfin(таблицы)
def get_html_min_m(url, params=None):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) (KHTML, like Gecko) Chrome/87.0.4280.66'}
    response = requests.get(url, headers=headers, params=params, verify=False)
    html = response.text
    return html


def get_pages_count_min_m(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        pagination = soup.find('a', class_='button_more').get("data-page-count")
        send_message_to_all_chats(bot, 'Всего страниц: ' + pagination)
        return int(pagination)
    except Exception:
        send_message_to_all_chats(bot, 'Количество страниц не найдено')


def get_content_min_m(html):
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', class_=['document_card inner_link', 'document_card inner_link important'])
    data = []
    my_bd_command.create_table_min()
    for block in blocks:
        try:
            link_doc = 'https://minfin.gov.ru' + block.get('data-href')
        except:
            link_doc = 'Ссылка на документ не найдена'

        try:
            tag = block.find('ul', class_='tag_list').get_text(strip=True)
        except:
            tag = 'Тег не найден'

        try:
            date_doc = block.find('span', class_='date').get_text(strip=True)
        except:
            date_doc = 'Дата опубликования не найдена'

        try:
            type_doc = block.find('a', class_='document_type').get_text(strip=True)
        except:
            type_doc = 'Тип документа не найден'

        try:
            title_doc = block.find('a', class_='document_title').get_text(strip=True) # Берем берем для проверки записей в БД
        except:
            title_doc = 'Заголовок документа не найден'

        try:
            file_info_doc = 'https://minfin.gov.ru' + block.find('a', class_='download_btn').get(
                'href')
        except:
            file_info_doc = 'Ссылка на файл не найдена'

        """Далее проваливаемся в ссылку карточки и берем оттуда ссылку на файл и данные о регистрации"""
        sub_page_soup = BeautifulSoup(get_html_min_m(link_doc), 'html.parser')
        try:
            reg = sub_page_soup.find('div', class_='page_description').get_text(strip=True)
        except:
            reg = 'Регистрационная информация не найдена'
        try:
            link_download = 'https://minfin.gov.ru' + sub_page_soup.find('a', class_='button_download').get('href')
        except:
            link_download = 'Доп. ссылка на файл не найдена'
        try:
            info_block = sub_page_soup.find('div', class_='document_data_information')
            spans = info_block.find_all('span', class_='t_mn2') if info_block else []
            date_update = spans[1].get_text(strip=True) if len(spans) >= 2 else 'Дата обновления не найдена' # берем срез второго класса
        except:
            date_update = 'Дата обновления не найдена'

        try:
            if my_bd_command.check_min(title_doc, date_update) == 0:
                my_bd_command.insert_min(link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg,
                                        link_download, date_update)
                data.append({
                    'Ссылка на документ': link_doc,
                    'Тег': tag,
                    'Дата опубликования': date_doc,
                    'Тип документа': type_doc,
                    'Заголовок документа': title_doc,
                    'Ссылка на файл': file_info_doc,
                    # Детализация документа
                    'Дата обновления': date_update,
                    'Зарегистрирован': reg,
                    'Доп. ссылка на файл:': link_download
                })
                send_message_to_all_chats(bot,
                                f'Свойство: {tag}\n'
                                f'Заголовок: {title_doc}\n'
                                f'Тип документа: {type_doc}\n'
                                f'Дата публикации: {date_doc.replace("Опубликовано: ", "")}\n'
                                f'Дата изменения: {date_update.replace("Изменено: ", "")}\n'
                                f'Регистрационная информация: {reg}\n'
                                'Ссылка: {link_doc}\n'
                                f'Ссылка на файл: {file_info_doc}\n'
                                f'Доп. ссылка на файл: {link_download}\n')
                send_message_to_all_chats(bot, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            send_message_to_all_chats(bot, '[X] Ошибка вставки данных в БД', ex)
            continue
    send_message_to_all_chats(bot, 'Количество новых документов: ' + str(len(data)))
    return data


def parser_min_m(url):
    pages = get_pages_count_min_m(get_html_min_m(url))
    data = []
    pages = 2  # берем для примера только 2 страницы
    for page in range(1, pages + 1):
        send_message_to_all_chats(bot, f'Сбор со страницы {page}')
        while True:
            try:
                data.extend(get_content_min_m(get_html_min_m(url, params={'page_65': page})))
                time.sleep(1)
                break
            except:
                send_message_to_all_chats(bot, 'Доступ прерван, ждем 5 сек.')
                for sec in range(1, 5):
                    time.sleep(1)
                    send_message_to_all_chats(bot, f'{sec}...')
                send_message_to_all_chats(bot, 'перезапуск')
    send_message_to_all_chats(bot, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


# parser_roskazna
def get_html_ros(url, params=None):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/87.0.4280.66 '
                    'Safari/537.36'
    }
    response = requests.get(url, headers=headers, params=params, verify=False)
    html = response.text
    return html

def get_pages_count_ros(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Находим количество страниц
    try:
        pagination = soup.find('div', class_='pagination').find_all('a')
        if pagination:
            pages = pagination[-2].text
        else:
            pages = 1
    except Exception:
        pages = 1
        send_message_to_all_chats(bot, 'Пагинация не найдена, страница будет обработана как единственная')

    send_message_to_all_chats(bot, 'Всего страниц: ' + str(pages))
    return int(pages)


def get_content_ros(html):
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find_all('div', class_='news-item')
    data = []
    my_bd_command.create_table_ros()
    for block in blocks:
        try:
            title = block.find('div', class_='news-info__name').get_text(strip=True)
        except:
            title = 'Заголовок документа не найден'

        try:
            publication = block.find('span', class_='date').get_text(strip=True)
        except:
            publication = 'Дата документа не найдена'

        try:
            pdf_link = 'https://www.roskazna.gov.ru/' + block.find('div', class_='news-info').find('a').get('href')
        except:
            pdf_link = 'Ссылка на PDF файл не найдена'

        try:
            if my_bd_command.check_ros(title) == 0:
                my_bd_command.insert_ros(title, publication, pdf_link)
                data.append({
                    'Заголовок документа': title,
                    'Дата документа': publication,
                    'Ссылка на PDF файл': pdf_link
                })
                send_message_to_all_chats(bot,
                                f'Заголовок документа: {title}\n'
                                f'Дата документа: {publication}\n'
                                f'Ссылка на PDF файл: {pdf_link}\n')
                send_message_to_all_chats(bot, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            send_message_to_all_chats(bot, '[X] Ошибка вставки данных в БД', ex)
            continue
    send_message_to_all_chats(bot, 'Количество новых документов: ' + str(len(data)))
    return data


def parser_ros(url):
    pages = get_pages_count_ros(get_html_ros(url))
    # Проходимся по все страницам и получаем данные
    data = []
    for page in range(1, int(pages) + 1):
        while True:
            try:
                html = get_html_ros(url, params={'PAGEN_1': page})
                send_message_to_all_chats(bot, f'Парсинг страницы {page} из {pages}...')
                data.extend(get_content_ros(html))
                # Выставим задержку между страницами, чтоб сайт не заблочил нас
                time.sleep(uniform(1, 2))
                break
            except:
                send_message_to_all_chats(bot, 'Доступ прерван, ждем 5 сек.')
                for sec in range(1, 5):
                    time.sleep(1)
                    send_message_to_all_chats(bot, f'{sec}...')
                send_message_to_all_chats(bot, 'перезапуск')
    send_message_to_all_chats(bot, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


#parser_Publication_gov
def fetch_documents(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def clean_text(text):
    if text:
        return text.replace('<br />', ' ').replace('\n', ' ').replace('\\', ' ')
    return text

def parse_documents(data):
    documents = []
    for item in data.get('items', []):
        view_date = item.get('viewDate', '')
        complex_name = clean_text(item.get('complexName', ''))
        document_date_str = item.get('documentDate', '')
        reg_number = item.get('jdRegNumber', '')
        document_date_reg_str = item.get('jdRegDate', '')
        pages_count = item.get('pagesCount', '')
        eo_number = item.get('eoNumber', '')
        link_doc = f"http://publication.pravo.gov.ru/document/{eo_number}"

        # Функция преобразования даты из формата YYYY-MM-DDTHH:MM:SS в DD-MM-YYYY
        def convert_date(date_str):
            if date_str:
                try:
                    # Проверяем специальный случай, когда дата равна '0001-01-01T00:00:00'
                    if date_str == '0001-01-01T00:00:00':
                        return 'Дата не определена'
                    return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S').strftime('%d.%m.%Y')
                except ValueError:
                    return 'Дата не определена'
            return 'Дата не определена'
        
        # Преобразования даты
        document_date = convert_date(document_date_str)
        document_date_reg = convert_date(document_date_reg_str)

        try:
            if my_bd_command.check_govp(complex_name) == 0:
                my_bd_command.insert_govp(view_date, complex_name, document_date, reg_number, document_date_reg, pages_count, eo_number, link_doc)
                documents.append({
                    'Дата публикации': view_date,
                    'Наименование документа': complex_name,
                    'Дата документа': document_date,
                    'Номер регистрации в Минюсте': reg_number,
                    'Дата регистрации в Минюсте': document_date_reg,
                    'Количество страниц в PDF файле документа': pages_count,
                    'Номер электронного опубликования': eo_number,
                    'Ссылка на документ': link_doc
                })
                send_message_to_all_chats(bot, 
                    f'Дата публикации: {view_date}\n'
                    f'Наименование документа: {complex_name}\n'
                    f'Дата документа: {document_date}\n'
                    f'Номер регистрации в Минюсте: {reg_number}\n'
                    f'Дата регистрации в Минюсте: {document_date_reg}\n'
                    f'Количество страниц в PDF файле документа: {pages_count}\n'
                    f'Номер электронного опубликования: {eo_number}\n'
                    f'Ссылка на документ: {link_doc}\n')
                send_message_to_all_chats(bot, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            send_message_to_all_chats(bot, '[X] Ошибка вставки данных в БД', ex)
            continue
    send_message_to_all_chats(bot, 'Количество новых документов: ' + str(len(documents)))
    return documents

def main(url):
    data = fetch_documents(url)
    if data:
        parsed_documents = parse_documents(data)

if __name__ == "__main__":
    main()
