import re  # мне показалось интересным решением сделать обработку запросов от пользователя через эту библиотеку.
# Вроде как мы из сообщения пользователя вырываем нужный шаблон, если он там есть и уже с ним работаем,
# эдакая "защита от дурака", да и пользователю можно формировать запрос более вольно, а нам, соответственно,
# меньше писанины в инструкциях. Но на практике всё оказалось не так радужно: среди тех, на ком тестировался конечный
# продукт, все предпочли, чтобы им просто показали шаблон запроса и даже нинкаких тестовых инструкций больше не надо
# и вольность написания запроса тоже особо никого не прильщает. Ну и ладно, изучение этого вопроса можно делегировать
# data-scientist'ам, а полученные мной в процессе работы знания точно лишними не будут)
import requests
import json
from config import *


class APIException(Exception):  # ошибка интернет-запроса
    pass


class UserRequestException(Exception):  # неверный запрос от пользователя
    pass


class SameValuesException(Exception):  # попытка сравнить две одинаковые валюты
    pass


class Converter:
    @staticmethod
    def convert(message):  # согласно заданию надо было назвать этот метод get_price(), но я забыл. В общем, это он
        try:
            message_form = re.fullmatch(r'[a-zA-Z]{3}\s*[,/|-]?\s*[a-zA-Z]{3}\s*[,/|-]?\s*\d+', message)  # изучая
            # эту библиотеку я заметил, что многие как главный её недостаток отмечают плохую читаемость шаблонов даже
            # для опытных программистов, поэтому расшифрую на всякий: мы ищем соответсвует ли введённый пользователем
            # текст следующему шаблону: 3 латинских буквы в любом регистре, неограниченное кол-во пробелов или их
            # отсутствие, 1 или 0 символов [,/|-], ещё раз сколько хочешь пробелов, потом ещё раз такая же
            # конструкция целиком и в конце одна или больше цифр. Таким образом запрос можно формировать максимально
            # вольно, главное чтобы он содержал 3-х буквенные обозначения валют.
            if message_form is not None:  # если шалость удалась, то функция возвращает нам объект соответствия. Сам
                # по себе он нам не нужен, для нас главное, что он не None
                formatted_message = re.sub(r'[,/|\s-]', "", message)  # отбрасываем всё ненужное, получая строку
                # формата btcusd909090 и уже её части проверяем на соответсвие имеющимся у нас валютам...
                base = formatted_message[0:3].upper() if formatted_message[0:3].upper() in value_list else None
                quote = formatted_message[3:6].upper() if formatted_message[3:6].upper() in value_list else None
                amount = int(formatted_message[6:]) if formatted_message[6:].isdigit() else None
                try:
                    if all([base, quote, amount]) is not None and base.upper() != quote.upper():  # ...и на
                        # несоответствие друг другу
                        payloads['fsym'] = base
                        payloads['tsyms'] = quote
                        req = requests.get(URL, params=payloads)  # ну и сложив все части пазла, отправляем таки
                        # запрос на сервер
                        try:
                            if req.status_code == 200:
                                total = json.loads(req.content)[quote] * amount
                                return f'{amount} {base} = {total} {quote}'
                            else:
                                raise APIException
                        except APIException:
                            return f'Что-то пошло не так. Код ответа: {req.status_code}'
                    else:
                        raise SameValuesException
                except SameValuesException:
                    return f'Введите две разных валюты для корректной конвертации'
            else:
                raise UserRequestException
        except UserRequestException:
            return f'Я не совсем Вас понял, повторите запрос или воспользуйтесь командами /help и /desc'
