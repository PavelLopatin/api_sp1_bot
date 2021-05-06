import os
import time

import requests
import telegram
from dotenv import load_dotenv
import logging

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    status = homework['status']
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось,' \
                  ' можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'})
        logging.info('Запрос удачный')
        return homework_statuses.json()
    except Exception as error:
        logging.exception(error)


def send_message(message, bot_client):
    logging.debug(f'Сообщение: {message} отправленно!')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logging.debug('Бот инициализизован.')
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(
                    new_homework.get('homeworks')[0]), bot_client)
                logging.info('Сообщение отправлено.')
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp)
            logging.info('Дату поменяли.')
            time.sleep(300)
        except Exception as e:
            logging.error(e, exc_info=True)
            text = f'Бот столкнулся с ошибкой: {e}'
            bot_client.send_message(chat_id=CHAT_ID, text=text)
            time.sleep(5)

if __name__ == '__main__':
    main()
