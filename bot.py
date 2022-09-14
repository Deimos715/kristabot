import config
import telebot
import requests
from bs4 import BeautifulSoup
import my_bd_command
import time
from random import uniform

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Основыне команды /start - Приветствие; /help - справка; /get_min_b - '
                                      'запрос документов с Минфина России (раздел бюджетной классификации).  '
                                      '/get_min_m - ''запрос документов с Минфина России (методический кабинет). '
                                      '/get_ros - запрос документов с Росказны (Письма о резервировании). ')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я бот-парсер. Помогу тебе запросить последние документы по бюджетной '
                                      'классифкации. Отправь /help для справки.')


@bot.message_handler(commands=['get_min_b'])
def update_message_min_b(message):
    # parser_minfin_budget
    bot.send_message(message.chat.id, 'Запрос данных с Минфина России (Приказы)')

    def get_html(url, params=None):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) (KHTML, like Gecko) Chrome/87.0.4280.66'}
        response = requests.get(url, headers=headers, params=params)
        html = response.text
        return html

    def get_pages_count(html):
        soup = BeautifulSoup(html, 'html.parser')
        try:
            pagination = soup.find('a', class_='button_more').get("data-page-count")
            bot.send_message(message.chat.id, 'Всего страниц: ' + pagination)
            return int(pagination)
        except Exception:
            bot.send_message(message.chat.id, 'Количество страниц не найдено')

    def get_content(html):
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
            sub_page_soup = BeautifulSoup(get_html(link_doc), 'html.parser')
            try:
                reg = sub_page_soup.find('div', class_='page_description').get_text(strip=True)
            except:
                reg = 'Регистрационная информация не найдена'
            try:
                link_download = 'https://minfin.gov.ru' + sub_page_soup.find('a', class_='download_btn').get('href')
            except:
                link_download = 'Доп. ссылка на файл не найдена'

            try:
                if my_bd_command.check_min(link_doc) == 0:
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
                    bot.send_message(message.chat.id,
                                     f'Ссылка: {link_doc}\n'
                                     f'Свойство: {tag}\n'
                                     f'Дата публикации: {date_doc.replace("Опубликовано: ", "")}\n'
                                     f'Тип документа: {type_doc}\nЗаголовок: {title_doc}\n'
                                     f'Ссылка на файл: {file_info_doc}\n'
                                     f'Регистрационная информация: {reg}\n'
                                     f'Доп. ссылка на файл: {link_download}\n')
                    bot.send_message(message.chat.id, '[INFO] Документ добавлен в БД')

            except Exception as ex:
                bot.send_message(message.chat.id, '[X] Ошибка вставки данных в БД', ex)
                continue
        bot.send_message(message.chat.id, 'Количество новых документов: ' + str(len(data)))
        return data

    def parser(url):
        pages = get_pages_count(get_html(url))
        data = []
        pages = 2  # берем для примера только 2 страницы
        for page in range(1, pages + 1):
            bot.send_message(message.chat.id, f'Сбор со страницы {page}')
            while True:
                try:
                    data.extend(get_content(get_html(url, params={'page_65': page})))
                    time.sleep(1)
                    break
                except:
                    bot.send_message(message.chat.id, 'Доступ прерван, ждем 5 сек.')
                    for sec in range(1, 5):
                        time.sleep(1)
                        bot.send_message(message.chat.id, f'{sec}...')
                    bot.send_message(message.chat.id, 'перезапуск')
        bot.send_message(message.chat.id, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')

    parser('https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/npa')


@bot.message_handler(commands=['get_min_m'])
def update_message_min_m(message):
    # parser_minfin_methodology
    bot.send_message(message.chat.id, 'Запрос данных с Минфина России (Приказы)')

    def get_html(url, params=None):
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) (KHTML, like Gecko) Chrome/87.0.4280.66'}
        response = requests.get(url, headers=headers, params=params)
        html = response.text
        return html

    def get_pages_count(html):
        soup = BeautifulSoup(html, 'html.parser')
        try:
            pagination = soup.find('a', class_='button_more').get("data-page-count")
            bot.send_message(message.chat.id, 'Всего страниц: ' + pagination)
            return int(pagination)
        except Exception:
            bot.send_message(message.chat.id, 'Количество страниц не найдено')

    def get_content(html):
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
            sub_page_soup = BeautifulSoup(get_html(link_doc), 'html.parser')
            try:
                reg = sub_page_soup.find('div', class_='page_description').get_text(strip=True)
            except:
                reg = 'Регистрационная информация не найдена'
            try:
                link_download = 'https://minfin.gov.ru' + sub_page_soup.find('a', class_='download_btn').get('href')
            except:
                link_download = 'Доп. ссылка на файл не найдена'

            try:
                if my_bd_command.check_min(link_doc) == 0:
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
                    bot.send_message(message.chat.id,
                                     f'Ссылка: {link_doc}\n'
                                     f'Свойство: {tag}\n'
                                     f'Дата публикации: {date_doc.replace("Опубликовано: ", "")}\n'
                                     f'Тип документа: {type_doc}\nЗаголовок: {title_doc}\n'
                                     f'Ссылка на файл: {file_info_doc}\n'
                                     f'Регистрационная информация: {reg}\n'
                                     f'Доп. ссылка на файл: {link_download}\n')
                    bot.send_message(message.chat.id, '[INFO] Документ добавлен в БД')

            except Exception as ex:
                bot.send_message(message.chat.id, '[X] Ошибка вставки данных в БД', ex)
                continue
        bot.send_message(message.chat.id, 'Количество новых документов: ' + str(len(data)))
        return data

    def parser(url):
        pages = get_pages_count(get_html(url))
        data = []
        pages = 2  # берем для примера только 2 страницы
        for page in range(1, pages + 1):
            bot.send_message(message.chat.id, f'Сбор со страницы {page}')
            while True:
                try:
                    data.extend(get_content(get_html(url, params={'page_65': page})))
                    time.sleep(1)
                    break
                except:
                    bot.send_message(message.chat.id, 'Доступ прерван, ждем 5 сек.')
                    for sec in range(1, 5):
                        time.sleep(1)
                        bot.send_message(message.chat.id, f'{sec}...')
                    bot.send_message(message.chat.id, 'перезапуск')
        bot.send_message(message.chat.id, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')

    parser('https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/metod')


@bot.message_handler(commands=['get_ros'])
def update_message_ros(message):
    # parser_roskazna
    bot.send_message(message.chat.id, 'Запрос данных с Росказны (Письма)')

    def get_html(url, params=None):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.66 '
                          'Safari/537.36'
        }
        response = requests.get(url, headers=headers, params=params)
        html = response.text
        return html

    def get_pages_count(html):
        soup = BeautifulSoup(html, 'html.parser')
        # Находим количество страниц
        try:
            pagination = soup.find('div', class_='pagination').find_all('a')
            if pagination:
                pages = pagination[-2].text
            else:
                pages = 1
            bot.send_message(message.chat.id, 'Всего страниц: ' + str(pages))
            return pages
        except Exception:
            bot.send_message(message.chat.id, 'Количество страниц не найдено')

    def get_content(html):
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
            except Exception as ex:
                bot.send_message(message.chat.id, '[X] Ошибка вставки данных в БД', ex)
                continue
        bot.send_message(message.chat.id, 'Количество новых документов: ' + str(len(data)))
        return data

    def parser(url):
        pages = get_pages_count(get_html(url))
        # Проходимся по все страницам и получаем данные
        data = []
        for page in range(1, int(pages) + 1):
            while True:
                try:
                    html = get_html(url, params={'PAGEN_1': page})
                    bot.send_message(message.chat.id, f'Парсинг страницы {page} из {pages}...')
                    data.extend(get_content(html))
                    # Выставим задержку между страницами, чтоб сайт не заблочил нас
                    time.sleep(uniform(1, 2))
                    break
                except:
                    bot.send_message(message.chat.id, 'Доступ прерван, ждем 5 сек.')
                    for sec in range(1, 5):
                        time.sleep(1)
                        bot.send_message(message.chat.id, f'{sec}...')
                    bot.send_message(message.chat.id, 'перезапуск')
        for i in data:
            bot.send_message(message.chat.id, (str(i).replace('{', '').replace('}', '').replace("'", "")))
        bot.send_message(message.chat.id, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')

    parser('https://www.roskazna.gov.ru/dokumenty/uchet-i-raspredelenie-postupleniy')


bot.polling()

if __name__ == '__main__':
    bot.polling(none_stop=True)
