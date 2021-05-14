import json
import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

TIME = 300
PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
PRAKTIKUM_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    status = {'reviewing': 'Работа взята в ревью',
              'approved': 'Ревьюеру всё понравилось,'
                          ' можно приступать к следующему уроку',
              'rejected': 'К сожалению в работе нашлись ошибки'}
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if 'status' not in homework or 'homework_name' not in homework:
        logging.error('Нет нужного ключа')
        return 'Нет нужного ключа'
    elif homework_name is None or homework['status'] is None:
        logging.error('Неверный статус или имя')
        return 'Неверный статус или имя'
    elif homework_status not in status:
        logging.error('Данного статуса нет в словаре')
        return 'Не удается получить статус домашнего задания' 
    verdict = status[homework_status]
    return f'У вас проверили работу "{homework_name}"!\n{verdict}.'


def get_homework_statuses(current_timestamp):
    try:
        homework_statuses = requests.get(
            PRAKTIKUM_URL,
            params={'from_date': current_timestamp},
            headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'})
        logging.info('Запрос удачный')
        return homework_statuses.json()
    except (requests.RequestException, json.decoder.JSONDecodeError) as error:
        logging.exception(error)
        return {}


def send_message(message, bot_client):
    logging.debug(f'Сообщение: {message} отправленно!')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot_client = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
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
            time.sleep(TIME)
        except Exception as e:
            logging.error(e, exc_info=True)
            text = f'Бот столкнулся с ошибкой: {e}'
            bot_client.send_message(chat_id=CHAT_ID, text=text)
            time.sleep(TIME)


if __name__ == '__main__':
    main()
