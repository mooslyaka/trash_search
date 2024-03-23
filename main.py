import telebot
from telebot import types
from PIL import Image

bot = telebot.TeleBot("7137374641:AAHuBp-BIcG6QiIaS7pDkCLzPG-UCjlAZao")


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Да!"))
    bot.send_message(message.chat.id, f"Здравствуйте, {message.from_user.first_name}, желаете ли вы оставить заявку?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, yes)


def yes(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    markup.add(button_geo)
    bot.send_message(message.chat.id, "Сначала отправте свою геолокацию", reply_markup=markup)


def write_coord(longitude, latitude):
    print("zxc")
    with open("coordinates.txt", "a") as file:
        file.write(f"{str(longitude)} {str(latitude)} \n")


@bot.message_handler(content_types=["location"])
def check_geo(message):
    markup = types.ReplyKeyboardMarkup()
    bot.send_message(message.chat.id, f"Геолокация принята! {message.location.longitude, message.location.latitude}")
    write_coord(message.location.longitude, message.location.latitude)
    bot.send_message(message.chat.id, "Теперь отправте фото неубранной мусорки")


@bot.message_handler(func=lambda m: True, content_types=["photo"])
def image(message):
    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    src = file_info.file_path
    with open(src, "wb") as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Ваше фото принято")

bot.polling(none_stop=True)
