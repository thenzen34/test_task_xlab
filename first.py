import wave
import contextlib
import os
import datetime
import sys

from tinkoff_voicekit_client import ClientSTT
from config import *
import logging

import psycopg2

error_log = logging.getLogger("errors")
error_log.setLevel(logging.INFO)
error_fh = logging.FileHandler("errors.log")
error_log.addHandler(error_fh)

recognizing_log = logging.getLogger("recognizing")
recognizing_log.setLevel(logging.INFO)
recognizing_fh = logging.FileHandler("recognizing.log")
recognizing_log.addHandler(recognizing_fh)

negative_words = ['нет', 'неудобно']
positive_words = ['говорите', 'да конечно', 'да', 'удобно']
ao_words = ['автоответчик']

'''
1 вас приветствует автоответчик оставьте сообщение после сигнала
2 алло говорите
3 ну да удобно его слушаю
4 нет я сейчас на работе до свидания
'''

'''
debug = False

def debug_echo(text):
    if debug:
        print(text)
'''


def find_word_in_text(words, text):
    """
    ищем первые вхождения слов в тексте
    :param words: список слов для поиска
    :type words: list
    :param text: слова которые сравниваем
    :type text: set
    """
    for word in words:
        if word in text:
            return True
    return False


def get_duration_wave_file(file_name):
    """
    вернем длительность wav файла
    :param file_name: имя файла
    :type file_name: str
    """
    with contextlib.closing(wave.open(file_name, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def write_result_to_db(result):
    """
    вернем длительность wav файла
    :param result: список колонок
    :type result: list
    """
    conn = psycopg2.connect(database=db_con_database, user=db_con_user,
                            password=db_con_password, host=db_con_host, port=db_con_port,
                            options=f'-c search_path={db_con_schema}')

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO recognizing_results' +
                            '(date, "time", id, result, phone_number, duration, recognizing_result) ' +
                            " VALUES ('{0}', '{1}', {2}, {3}, '{4}', {5}, '{6}')".format(
                                result[0],
                                result[1],
                                result[2],
                                result[3],
                                result[4],
                                result[5],
                                result[6],
                            ))
    finally:
        conn.close()


def main():
    params = sys.argv
    if len(params) < 5:
        print("need path_to_wav phone_number write_to_db stage_recognizing")
        return
    path_to_wav = params[1]
    phone_number = params[2]
    write_to_db = params[3] == "1"
    stage_recognizing = 1 if params[4] == "1" else 2

    client = ClientSTT(API_KEY, SECRET_KEY)

    audio_config = {
        "encoding": "LINEAR16",
        "sample_rate_hertz": 8000,
        "num_channels": 1
    }
    stream_config = {"config": audio_config}

    recognizing_result = ""
    result = 0
    duration = get_duration_wave_file(path_to_wav)

    # делаем запрос на распознование
    with open(path_to_wav, "rb") as source:
        responses = client.streaming_recognize(source, stream_config)
        for response in responses:
            text_result = response[0]['recognition_result']['alternatives'][0]['transcript']
            text_words = set(text_result.lower().split())

            if len(text_words) == 0:
                continue

            recognizing_result = text_result

            if stage_recognizing == 1:
                if find_word_in_text(ao_words, text_words):
                    result = 0
                    # debug_echo("автоответчик")
                else:
                    result = 1
                    # debug_echo("человек")
            else:
                if find_word_in_text(negative_words, text_words):
                    result = 0
                    # debug_echo("негатив")
                elif find_word_in_text(positive_words, text_words):
                    result = 1
                    # debug_echo("позитив")

    now = datetime.datetime.now()
    uniq_id = now.strftime('%s')  # уникальный id для лога и БД это таймстамп
    result_data = [
        now.strftime('%Y-%m-%d'),
        now.strftime('%H:%M:%S'),
        uniq_id,
        result,
        phone_number,
        duration,
        recognizing_result
    ]
    recognizing_log.info('\t'.join(str(x) for x in result_data))

    if write_to_db:
        write_result_to_db(result_data)

    # удаляем переданный файл
    if delete_wav_file:
        os.remove(path_to_wav)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        error_log.error(str(e))
