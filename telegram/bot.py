import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from AI.ai_handler import ai_parse_text
from utils import parse_json_to_bot_answer, manage_events
from Credentials.CredentialsFunctions import check_user_credentials, create_authorization_url, get_user_credential


load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

markup = InlineKeyboardMarkup(row_width=2)
markup.add(
    InlineKeyboardButton("Yes", callback_data='yes'),
    InlineKeyboardButton("No", callback_data='no')
)

login_markup = InlineKeyboardMarkup()
login_markup.add(InlineKeyboardButton("Login", callback_data="login"))

users_input = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if (check_user_credentials(message.from_user.id)):
        bot.send_message(message.chat.id, "Siema chłopie. Co mogę dla ciebie dziś zrobić?")
    else:
        bot.send_message(message.chat.id, "Siema nie mam twoich danych, weź się zaloguj", reply_markup=login_markup)


@bot.message_handler(content_types=['text'])
def send_command_message(message):
    if (not check_user_credentials(message.from_user.id)):
        bot.send_message(message.chat.id, "Nie jesteś zalogowany proszę się zaloguj ", reply_markup=login_markup)
    else:
        users_input[message.from_user.id] = ai_parse_text(message.text)
        bot_answer = parse_json_to_bot_answer(users_input[message.from_user.id])
        if (bot_answer != None):
            bot.send_message(message.chat.id, f"{bot_answer} \n\nDokładnie to ode mnie chcesz?", reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "Debilu wprowadź sensowne dane")

@bot.callback_query_handler(func=lambda call:call.data in ["yes", "no", "login"])
def send_callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "No dobra już robię")
        result = manage_events(users_input[call.from_user.id], call.from_user.id)
        if (result):
            bot.send_message(call.message.chat.id, result)
        bot.send_message(call.message.chat.id, "Zrobione. Chcesz jeszcze coś?")
    elif call.data == "no":
        bot.edit_message_text("No to co ty chcesz. Weź napisz", chat_id=call.message.chat.id, message_id=call.message.id)
    elif call.data == "login":
        create_authorization_url(call.from_user.id)


if __name__ == "__main__":
    bot.infinity_polling()



