import os
import time
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from AppFunctions import auth_into_db
from AI.ai_handler import ai_parse_text
from utils import parse_json_to_bot_answer

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
    auth_into_db(message.from_user.id)
    bot.send_message(message.chat.id, "Siema chłopie. Co mogę dla ciebie dziś zrobić?")


@bot.message_handler(content_types=['text'])
def send_command_message(message):
    ai_text_parsed = ai_parse_text(message.text)
    bot_answer = parse_json_to_bot_answer(ai_text_parsed)
    if (bot_answer != None):
        bot.send_message(message.chat.id, f"{bot_answer} \n\nDokładnie to ode mnie chcesz?", reply_markup=markup, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Debilu wprowadź sensowne dane")
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



