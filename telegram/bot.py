import os
import time

from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

blocked_chats = []

markup = InlineKeyboardMarkup(row_width=2)
markup.add(
    InlineKeyboardButton("Yes", callback_data='yes'),
    InlineKeyboardButton("No", callback_data='no')
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    #print(message.from_user.first_name)
    #print(message.from_user.id)
    bot.send_message(message.chat.id, "Siema chłopie. Co mogę dla ciebie dziś zrobić?")


@bot.message_handler(content_types=['text'])
def send_command_message(message):
    bot.send_message(message.chat.id, f"{message.text} \n\nDokładnie to ode mnie chcesz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call:call.data in ["yes", "no"])
def send_callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "No dobra już robię")
        time.sleep(3)
        bot.send_message(call.message.chat.id, "Zrobione. Chcesz jeszcze coś?")
    elif call.data == "no":
        bot.edit_message_text("No to co ty chcesz. Weź napisz", chat_id=call.message.chat.id, message_id=call.message.id)

bot.infinity_polling()



