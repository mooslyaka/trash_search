from telebot import types
import os
import telebot

bot = telebot.TeleBot("7016202494:AAEutxmMaJuTvAJS184seuOFgKVF3lxyWUs")
list_managers = ["mooslyaka"]



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
            write_coord(str(call.data).split()[1], str(call.data).split()[2], str(call.data).split()[3],
                        str(call.data).split()[4])
        if str(call.data).split()[0] == "0":
            os.remove(f'{str(call.data).split()[1]}')


def check_photo(message, file, longitude, latitude, year, time):
    image = open(file, "rb")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Одобрить", callback_data=f"1 {longitude} {latitude} {year} {time}"))
    markup.add(types.InlineKeyboardButton("Отклонить", callback_data=f"0 {file}"))
    bot.send_photo(message.chat.id, photo=image, reply_markup=markup)


def write_coord(longitude, latitude, year, time):
    with open("coordinates.txt", "a") as file:
        file.write(f"{str(longitude)} {str(latitude)} {str(year)} {str(time)}\n")


@bot.message_handler(content_types=["text"])
def text(message):
    if message.text == "Проверять!":
        file = open("all_coordinates.txt", 'r')
        list_coords = file.readlines()
        if list_coords:
            for i in list_coords:
                i = i.split()
                check_photo(message, i[0], i[1], i[2], {i[3]}, {i[4]})


bot.polling(none_stop=True)
