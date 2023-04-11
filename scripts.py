import requests
import telebot
import config
from bs4 import BeautifulSoup
import my_bd_command
import time
from random import uniform

bot = telebot.TeleBot(config.token)


# parser_minfin(приказы)
def get_html_min_b(url, params=None):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) (KHTML, like Gecko) Chrome/87.0.4280.66'}
    response = requests.get(url, headers=headers, params=params)
    html = response.text
    return html


def get_pages_count_min_b(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        pagination = soup.find('a', class_='button_more').get("data-page-count")
        bot.send_message(355908770, 'Всего страниц: ' + pagination)
        return int(pagination)
    except Exception:
        bot.send_message(355908770, 'Количество страниц не найдено')


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
            title_doc = block.find('p', class_='document_title').get_text(strip=True)
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
            if my_bd_command.check_min(file_info_doc) == 0:
                my_bd_command.insert_min(link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg,
                                         link_download)
                data.append({
                    'Ссылка на документ': link_doc,
                    'Тег': tag,
                    'Дата опубликования': date_doc,
                    'Тип документа': type_doc,
                    'Заголовок документа': title_doc,
                    'Ссылка на файл': file_info_doc,
                    # Детализация документа
                    'Зарегистрирован': reg,
                    'Доп. ссылка на файл:': link_download
                })
                bot.send_message(355908770,
                                 f'Свойство: {tag}\n'
                                 f'Заголовок: {title_doc}\n'
                                 f'Тип документа: {type_doc}\n'
                                 f'Дата публикации: {date_doc.replace("Опубликовано: ", "")}\n'
                                 f'Регистрационная информация: {reg}\n'
                                 f'Ссылка: {link_doc}\n'
                                 f'Ссылка на файл: {file_info_doc}\n'
                                 f'Доп. ссылка на файл: {link_download}\n')
                bot.send_message(355908770, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            bot.send_message(355908770, '[X] Ошибка вставки данных в БД', ex)
            continue
    bot.send_message(355908770, 'Количество новых документов: ' + str(len(data)))
    return data


def parser_min_b(url):
    pages = get_pages_count_min_b(get_html_min_b(url))
    data = []
    pages = 2  # берем для примера только 2 страницы
    for page in range(1, pages + 1):
        bot.send_message(355908770, f'Сбор со страницы {page}')
        while True:
            try:
                data.extend(get_content_min_b(get_html_min_b(url, params={'page_65': page})))
                time.sleep(1)
                break
            except:
                bot.send_message(355908770, 'Доступ прерван, ждем 5 сек.')
                for sec in range(1, 5):
                    time.sleep(1)
                    bot.send_message(355908770, f'{sec}...')
                bot.send_message(355908770, 'перезапуск')
    bot.send_message(355908770, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


# parser_minfin(таблицы)
def get_html_min_m(url, params=None):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) (KHTML, like Gecko) Chrome/87.0.4280.66'}
    response = requests.get(url, headers=headers, params=params)
    html = response.text
    return html


def get_pages_count_min_m(html):
    soup = BeautifulSoup(html, 'html.parser')
    try:
        pagination = soup.find('a', class_='button_more').get("data-page-count")
        bot.send_message(355908770, 'Всего страниц: ' + pagination)
        return int(pagination)
    except Exception:
        bot.send_message(355908770, 'Количество страниц не найдено')


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
            title_doc = block.find('p', class_='document_title').get_text(strip=True)
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
            link_download = 'https://minfin.gov.ru' + sub_page_soup.find('a', class_='download_btn').get('href')
        except:
            link_download = 'Доп. ссылка на файл не найдена'

        try:
            if my_bd_command.check_min(file_info_doc) == 0:
                my_bd_command.insert_min(link_doc, tag, date_doc, type_doc, title_doc, file_info_doc, reg,
                                         link_download)
                data.append({
                    'Ссылка на документ': link_doc,
                    'Тег': tag,
                    'Дата опубликования': date_doc,
                    'Тип документа': type_doc,
                    'Заголовок документа': title_doc,
                    'Ссылка на файл': file_info_doc,
                    # Детализация документа
                    'Зарегистрирован': reg,
                    'Доп. ссылка на файл:': link_download
                })
                bot.send_message(355908770,
                                 f'Свойство: {tag}\n'
                                 f'Заголовок: {title_doc}\n'
                                 f'Тип документа: {type_doc}\n'
                                 f'Дата публикации: {date_doc.replace("Опубликовано: ", "")}\n'
                                 f'Регистрационная информация: {reg}\n'
                                 f'Ссылка: {link_doc}\n'
                                 f'Ссылка на файл: {file_info_doc}\n'
                                 f'Доп. ссылка на файл: {link_download}\n')
                bot.send_message(355908770, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            bot.send_message(355908770, '[X] Ошибка вставки данных в БД', ex)
            continue
    bot.send_message(355908770, 'Количество новых документов: ' + str(len(data)))
    return data


def parser_min_m(url):
    pages = get_pages_count_min_m(get_html_min_m(url))
    data = []
    pages = 2  # берем для примера только 2 страницы
    for page in range(1, pages + 1):
        bot.send_message(355908770, f'Сбор со страницы {page}')
        while True:
            try:
                data.extend(get_content_min_m(get_html_min_m(url, params={'page_65': page})))
                time.sleep(1)
                break
            except:
                bot.send_message(355908770, 'Доступ прерван, ждем 5 сек.')
                for sec in range(1, 5):
                    time.sleep(1)
                    bot.send_message(355908770, f'{sec}...')
                bot.send_message(355908770, 'перезапуск')
    bot.send_message(355908770, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


# parser_roskazna
def get_html_ros(url, params=None):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/87.0.4280.66 '
                      'Safari/537.36'
    }
    response = requests.get(url, headers=headers, params=params)
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
        bot.send_message(355908770, 'Всего страниц: ' + str(pages))
        return pages
    except Exception:
        bot.send_message(355908770, 'Количество страниц не найдено')


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
                bot.send_message(355908770,
                                 f'Заголовок документа: {title}\n'
                                 f'Дата документа: {publication}\n'
                                 f'Ссылка на PDF файл: {pdf_link}\n')
                bot.send_message(355908770, '[INFO] Документ добавлен в БД')

        except Exception as ex:
            bot.send_message(355908770, '[X] Ошибка вставки данных в БД', ex)
            continue
    bot.send_message(355908770, 'Количество новых документов: ' + str(len(data)))
    return data


def parser_ros(url):
    pages = get_pages_count_ros(get_html_ros(url))
    # Проходимся по все страницам и получаем данные
    data = []
    for page in range(1, int(pages) + 1):
        while True:
            try:
                html = get_html_ros(url, params={'PAGEN_1': page})
                bot.send_message(355908770, f'Парсинг страницы {page} из {pages}...')
                data.extend(get_content_ros(html))
                # Выставим задержку между страницами, чтоб сайт не заблочил нас
                time.sleep(uniform(1, 2))
                break
            except:
                bot.send_message(355908770, 'Доступ прерван, ждем 5 сек.')
                for sec in range(1, 5):
                    time.sleep(1)
                    bot.send_message(355908770, f'{sec}...')
                bot.send_message(355908770, 'перезапуск')
    bot.send_message(355908770, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')
