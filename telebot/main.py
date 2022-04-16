import telebot
from extensions import *

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start_help(message: telebot.types.Message):
    bot.send_message(message.chat.id, f"Я могу помочь конвертировать валюту в соответствии с актуальным курсом: "
                                      f"просто введите названия валют и сумму конвертации "
                                      f"\nЧтобы подробнее узнать о принципе работы бота воспользуйтесь командой "
                                      f"/desc \nЧтобы посмотреть список доступных валют воспользуйтесь командой "
                                      f"/values")


@bot.message_handler(commands=['desc'])
def description(message: telebot.types.Message):
    bot.send_message(message.chat.id, f'Запрос должен содержать названия валют в любом регистре и сумму конвертации '
                                      f'целым числом. Доступные валюты можно посмотреть по команде /values\nЧтобы '
                                      f'вывод был более удобным для чтения старайтесь конвертировать бОльшие валюты в'
                                      f'меньшие или придерживайтесь правила "Биткоин всегда первый, рубль всегда '
                                      f'последний"')


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    output = []
    for i in value_list:
        output.append(i)
        output.append('\n')
    bot.send_message(message.chat.id, ''.join(output))


@bot.message_handler(content_types=['text'])
def main_handler(message: telebot.types.Message):
    bot.send_message(message.chat.id, Converter.convert(message.text))


if __name__ == "__main__":
    bot.polling(non_stop=True)
