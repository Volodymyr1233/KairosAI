import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from AI.ai_handler import ai_parse_text
from utils import parse_json_to_bot_answer, manage_events, construct_events, generate_indexes, update_event
from Credentials.CredentialsFunctions import check_user_credentials, create_authorization_url, get_user_credential
from AI.event_schema import EventType
from GoogleAPI.GoogleCalendarAPI import deleteEvent
from Credentials.CredentialsFunctions import get_user_credential


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

@bot.message_handler(func=lambda mess: f"{mess.from_user.id}_generated_remove_indexes" in users_input and mess.text in users_input[f"{mess.from_user.id}_generated_remove_indexes"])
def send_remove_answer(message):
    if (message.text == "Anuluj"):
        bot.send_message(message.from_user.id, "Ewenty nie zostały usunięte", reply_markup=ReplyKeyboardRemove())
    else:
        remove_index = int(message.text) - 1
        deleteEvent(get_user_credential(message.from_user.id), users_input[f"{message.from_user.id}_events_to_delete"][remove_index])
        bot.send_message(message.from_user.id, "Ewent został usunięty", reply_markup=ReplyKeyboardRemove())
    del users_input[f"{message.from_user.id}_events_to_delete"]
    del users_input[f"{message.from_user.id}_generated_remove_indexes"]
    del users_input[message.from_user.id]

@bot.message_handler(func=lambda mess: f"{mess.from_user.id}_generated_update_indexes" in users_input and mess.text in users_input[f"{mess.from_user.id}_generated_update_indexes"])
def send_update_answer(message):
    if (message.text == "Anuluj"):
        bot.send_message(message.from_user.id, "Żaden ewent nie został zaktualizowany!", reply_markup=ReplyKeyboardRemove())
    else:
        update_index = int(message.text) - 1
        update_event(message.from_user.id, users_input[f"{message.from_user.id}_events_to_update"][update_index], users_input[message.from_user.id])
        bot.send_message(message.from_user.id, "Ewent został zaktualizowany", reply_markup=ReplyKeyboardRemove())
    del users_input[f"{message.from_user.id}_events_to_update"]
    del users_input[f"{message.from_user.id}_generated_update_indexes"]
    del users_input[message.from_user.id]


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

        if (isinstance(result, str)):
            bot.send_message(call.message.chat.id, result)
        else:
            bot.send_message(call.message.chat.id, construct_events(result))
        if (users_input[call.from_user.id]["event_type"] == EventType.REMOVE.value):
            delete_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            generated_indexes = generate_indexes(result)
            generated_indexes.append("Anuluj")
            users_input[f"{call.from_user.id}_events_to_delete"] = result
            users_input[f"{call.from_user.id}_generated_remove_indexes"] = generated_indexes
            delete_markup.add(*generated_indexes)
            bot.send_message(call.message.chat.id, "Wybierz wydarzenie żeby usunąć", reply_markup=delete_markup)
        elif (users_input[call.from_user.id]["event_type"] == EventType.EDIT.value):
            update_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            generate_update_indexes = generate_indexes(result)
            generate_update_indexes.append("Anuluj")
            users_input[f"{call.from_user.id}_events_to_update"] = result
            users_input[f"{call.from_user.id}_generated_update_indexes"] = generate_update_indexes
            update_markup.add(*generate_update_indexes)
            bot.send_message(call.message.chat.id, "Wybierz wydarzenie które chcesz zaktualizować", reply_markup=update_markup)
    elif call.data == "no":
        bot.edit_message_text("No to co ty chcesz. Weź napisz", chat_id=call.message.chat.id, message_id=call.message.id)
    elif call.data == "login":
        create_authorization_url(call.from_user.id)


if __name__ == "__main__":
    bot.infinity_polling()



