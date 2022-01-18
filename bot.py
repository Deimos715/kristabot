import config
import telebot
import requests
from bs4 import BeautifulSoup
import my_bd_command

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
    url = 'https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/#'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 '
                      'Safari/537.36'
    }
    data = []
    pages = 2
    for page in range(1, int(pages) + 1):
        # передаем наши headers и params, где params словарь с параметром ключ:значение(page:'номер страницы')
        response = requests.get(url, headers=headers, params={'page_57': page})
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        blocks = soup.find_all('div', class_='doc-view-item doc-view ajax-link')[0:4]
        bot.send_message(message.chat.id, f'Парсинг страницы {page} из {pages}...')

        my_bd_command.create_table_min()

        for block in blocks:
            title = block.find('p', class_='dvi-type').get_text(strip=True)
            date_doc = block.find('p', class_='dvi-stats').get_text(strip=True)
            description = block.find('p', class_='dvi-title').get_text(strip=True)
            try:
                status = block.find('p', class_='new-list-text new-list-announce').get_text(strip=True)
            except Exception:
                status = 'нет данных'
            publication = block.find('dl', class_='doc-view-dates').get_text(strip=True)
            try:
                link_view = 'https://minfin.gov.ru/' + block.find('div', class_='dvi-plus').find('a').get('href'),
            except Exception:
                link_view = 'нет данных'
            doc_link_one = 'https://minfin.gov.ru/' + block.find('div',
                                                                 class_='doc-view-actions').find('span').find('a').get(
                'href')
            try:
                doc_link_two = 'https://minfin.gov.ru/' + block.find('a', class_='icon-link icon-link_download').get(
                    'href'),
            except Exception:
                doc_link_two = 'нет данных'

            try:
                if my_bd_command.check_min(doc_link_one) == 0:
                    my_bd_command.insert_min(title, date_doc, description, status, publication, link_view, doc_link_one,
                                             doc_link_two)
                    data.append({
                        'title': title,
                        'date_doc': date_doc,
                        'description': description,
                        'status': status,
                        'publication': publication,
                        'link_view': link_view,
                        'doc_link_one': doc_link_one,
                        'doc_link_two': doc_link_two
                    })
                    bot.send_message(message.chat.id, '[INFO] Документ добавлен в БД')

            except Exception as ex:
                bot.send_message(message.chat.id, '[X] Ошибка вставки данных в БД', ex)
                continue
    bot.send_message(message.chat.id, 'Количество новых документов: ' + str(len(data)))

    for i in data:
        bot.send_message(message.chat.id, (str(i).replace('{', '').replace('}', '').replace("'", "")))

    bot.send_message(message.chat.id, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


@bot.message_handler(commands=['get_min_m'])
def update_message_min_m(message):
    # parser_minfin_methodology
    bot.send_message(message.chat.id, 'Запрос данных с Минфина России (Таблицы соответствия)')
    url = 'https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/#'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 '
                      'Safari/537.36'
    }
    data = []
    pages = 2
    for page in range(1, int(pages) + 1):
        # передаем наши headers и params, где params словарь с параметром ключ:значение(page:'номер страницы')
        response = requests.get(url, headers=headers, params={'page_38': page})
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        blocks = soup.find_all('div', class_='doc-view-item doc-view ajax-link')[4:10]
        bot.send_message(message.chat.id, f'Парсинг страницы {page} из {pages}...')

        my_bd_command.create_table_min()

        for block in blocks:
            title = block.find('p', class_='dvi-type').get_text(strip=True)
            date_doc = block.find('p', class_='dvi-stats').get_text(strip=True)
            description = block.find('p', class_='dvi-title').get_text(strip=True)
            try:
                status = block.find('p', class_='new-list-text new-list-announce').get_text(strip=True)
            except Exception:
                status = 'нет данных'
            publication = block.find('dl', class_='doc-view-dates').get_text(strip=True)
            try:
                link_view = 'https://minfin.gov.ru/' + block.find('div', class_='dvi-plus').find('a').get('href'),
            except Exception:
                link_view = 'нет данных'
            doc_link_one = 'https://minfin.gov.ru/' + block.find('div',
                                                                 class_='doc-view-actions').find('span').find('a').get(
                'href')
            try:
                doc_link_two = 'https://minfin.gov.ru/' + block.find('a', class_='icon-link icon-link_download').get(
                    'href'),
            except Exception:
                doc_link_two = 'нет данных'

            try:
                if my_bd_command.check_min(doc_link_one) == 0:
                    my_bd_command.insert_min(title, date_doc, description, status, publication, link_view, doc_link_one,
                                             doc_link_two)
                    data.append({
                        'title': title,
                        'date_doc': date_doc,
                        'description': description,
                        'status': status,
                        'publication': publication,
                        'link_view': link_view,
                        'doc_link_one': doc_link_one,
                        'doc_link_two': doc_link_two
                    })
                    bot.send_message(message.chat.id, '[INFO] Документ добавлен в БД')

            except Exception as ex:
                bot.send_message(message.chat.id, '[X] Ошибка вставки данных в БД', ex)
                continue
    bot.send_message(message.chat.id, 'Количество новых документов: ' + str(len(data)))

    for i in data:
        bot.send_message(message.chat.id, (str(i).replace('{', '').replace('}', '').replace("'", "")))

    bot.send_message(message.chat.id, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


@bot.message_handler(commands=['get_ros'])
def update_message_ros(message):
    # parser_roskazna
    bot.send_message(message.chat.id, 'Запрос данных с Росказны (Письма)')
    url = 'https://www.roskazna.gov.ru/dokumenty/uchet-i-raspredelenie-postupleniy/'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 '
                      'Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    # pagination = soup.find('div', class_='pagination').find_all('a')
    # if pagination:
    #     pages = pagination[-2].text
    # else:
    #     pages = 1
    # bot.send_message(message.chat.id, 'Всего страниц: ' + pages)
    try:
        pagination = soup.find('div', class_='pagination').find_all('a')
        pages = pagination[-2].text
    except:
        pages = 1
    bot.send_message(message.chat.id, f'Всего страниц: {pages}')
    data = []
    for page in range(1, int(pages) + 1):
        response = requests.get(url, headers=headers, params={'PAGEN_1': page})
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        blocks = soup.find_all('div', class_='news-item')
        bot.send_message(message.chat.id, f'парсинг страницы {page} из {pages}...')

        my_bd_command.create_table_ros()

        for block in blocks:
            title = block.find('div', class_='news-info__name').get_text(strip=True).replace('\xa0', ' ').replace('\r\n'
                                                                                                                  , ' ')
            publication = block.find('span', class_='date').get_text(strip=True)
            pdf_link = 'https://www.roskazna.gov.ru/' + block.find('div', class_='news-info').find('a').get('href')

            try:
                if my_bd_command.check_ros(title) == 0:
                    my_bd_command.insert_ros(title, publication, pdf_link)
                    data.append({
                        'title': title,
                        'publication': publication,
                        'pdf_link': pdf_link
                    })
                    bot.send_message(message.chat.id, '[INFO] Письмо добавлено в БД')

            except Exception as ex:
                bot.send_message(message.chat.id, '[X] Ошибка вставки данных в БД', ex)
                continue

    bot.send_message(message.chat.id, 'Количество новых документов: ' + str(len(data)))

    for ros in data:
        bot.send_message(message.chat.id, (str(ros).replace('{', '').replace('}', '').replace("'", "")))

    bot.send_message(message.chat.id, 'Получено ' + str(len(data)) + ' позиций(-я, -и)')


bot.polling()

if __name__ == '__main__':
    bot.polling(none_stop=True)
