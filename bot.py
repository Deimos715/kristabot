import config
import telebot
import datetime
import time
import schedule
import threading
import scripts

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
    url = 'https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/npa'

    bot.send_message(message.chat.id, 'Запрос данных с Минфина России (Приказы)')

    html = scripts.get_html_min_b(url)

    scripts.get_pages_count_min_b(html)

    scripts.get_content_min_b(html)

    scripts.parser_min_b(url)


@bot.message_handler(commands=['get_min_m'])
def update_message_min_m(message):
    # parser_minfin_methodology
    url = 'https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/metod'

    bot.send_message(message.chat.id, 'Запрос данных с Минфина России (Приказы)')

    html = scripts.get_html_min_m(url)

    scripts.get_pages_count_min_m(html)

    scripts.get_content_min_m(html)

    scripts.parser_min_m(url)


@bot.message_handler(commands=['get_ros'])
def update_message_ros(message):
    # parser_roskazna
    url = 'https://www.roskazna.gov.ru/dokumenty/uchet-i-raspredelenie-postupleniy'

    bot.send_message(message.chat.id, 'Запрос данных с Росказны (Письма)')

    html = scripts.get_html_ros(url)

    scripts.get_pages_count_ros(html)

    scripts.get_content_ros(html)

    scripts.parser_ros(url)


def scheduled_task_min_b():
    print('запуск')
    bot.send_message(355908770, 'Начало выполнения задачи. Минфин - бюджет')
    scripts.parser_min_b('https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/npa')
    bot.send_message(355908770, 'Задача выполнена')
    bot.send_message(355908770, '****************')


def scheduled_task_min_m():
    print('запуск')
    bot.send_message(355908770, 'Начало выполнения задачи. Минфин - метод кабинет')
    scripts.parser_min_m('https://minfin.gov.ru/ru/perfomance/budget/classandaccounting/metod')
    bot.send_message(355908770, 'Задача выполнена')
    bot.send_message(355908770, '****************')


def scheduled_task_ros():
    print('запуск')
    bot.send_message(355908770, 'Начало выполнения задачи. Росказна')
    scripts.parser_ros('https://www.roskazna.gov.ru/dokumenty/uchet-i-raspredelenie-postupleniy')
    bot.send_message(355908770, 'Задача выполнена')
    bot.send_message(355908770, '****************')


def scheduler():
    schedule.every().day.at("07:00").do(scheduled_task_min_b)
    schedule.every().day.at("07:05").do(scheduled_task_min_m)
    schedule.every().day.at("07:10").do(scheduled_task_ros)
    while True:
        now = datetime.datetime.now()
        # Проверяем, является ли текущий день рабочим днем
        if now.weekday() in range(0, 5):
            schedule.run_pending()
        time.sleep(1)


start_func = threading.Thread(target=scheduler)

if __name__ == '__main__':
    start_func.start()
    bot.polling(none_stop=True)
