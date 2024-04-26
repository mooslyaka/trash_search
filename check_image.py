import telebot
from telebot import types
import os

bot = telebot.TeleBot("7016202494:AAEutxmMaJuTvAJS184seuOFgKVF3lxyWUs")
list_managers = ["mooslyaka"]
msg = None
image = None
def check_man(message):
    if message.from_user.first_name in list_managers:
        return True
    else:
        bot.send_message(message.chat.id,
                         f"Здравствуйте, у вас нет доступа к этому боту")


@bot.message_handler(commands=["start"])
def start(message):
    if check_man(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Проверять!"))
        bot.send_message(message.chat.id,
                         f"Здравствуйте, {message.from_user.first_name}, начать проверять заявки?",
                         reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if str(call.data).split()[0] == "1":
            write_coord(str(call.data).split()[1], str(call.data).split()[2])


def check_photo(message, file, longitude, latitude):
    global msg, image
    image = open(file, "rb")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Одобрить", callback_data=f"1 {longitude} {latitude}"))
    markup.add(types.InlineKeyboardButton("Отклонить", callback_data="0"))
    msg = bot.send_photo(message.chat.id, photo=image, reply_markup=markup)


def write_coord(longitude, latitude):
    with open("coordinates.txt", "a") as file:
        file.write(f"{str(longitude)} {str(latitude)}\n")


@bot.message_handler(content_types=["text"])
def text(message):
    if message.text == "Одобрить":
        write_coord()
    if message.text == "Проверять!":
        file = open("all_coordinates.txt", 'r')
        list_coords = file.readlines()
        print(list_coords)
        if list_coords:
            for i in list_coords:
                i = i.split()
                print("ASD")
                check_photo(message, i[2], i[0], i[1])


bot.polling(none_stop=True)
