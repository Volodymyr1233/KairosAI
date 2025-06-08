import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from AI.ai_handler import ai_parse_text
from utils import parse_json_to_bot_answer, manage_events, construct_events, generate_indexes, update_event
from Credentials.CredentialsFuntions_online import check_user_credentials, create_authorization_url, get_user_credential
from AI.event_schema import EventType
from GoogleAPI.GoogleCalendarAPI import deleteEvent, Reminder
from Credentials.CredentialsFuntions_online import get_user_credential
import time
import threading
from utils import construct_events


load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

markup = InlineKeyboardMarkup(row_width=2)
markup.add(
    InlineKeyboardButton("Yes", callback_data='yes'),
    InlineKeyboardButton("No", callback_data='no')
)




users_input = {}

user_chat_id = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_chat_id[message.from_user.id] = message.chat.id
    login_markup = InlineKeyboardMarkup()
    login_markup.add(InlineKeyboardButton("Login", url=create_authorization_url(message.from_user.id)))
    if (check_user_credentials(message.from_user.id)):
        bot.send_message(message.chat.id, "Cześć! Jak mogę ci dziś pomóc? 😊")
    else:
        bot.send_message(message.chat.id,  "Hej! Wygląda na to, że nie jesteś zalogowany. Kliknij poniżej, aby się zalogować ⬇️", reply_markup=login_markup)

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
    login_markup = InlineKeyboardMarkup()
    login_markup.add(InlineKeyboardButton("Login", url=create_authorization_url(message.from_user.id)))
    if (not check_user_credentials(message.from_user.id)):
        bot.send_message(message.chat.id, "Ups! Nie mam jeszcze Twoich danych. Prosze się zaloguj...⬇️", reply_markup=login_markup)
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
        bot.edit_message_text("No dobra już robię", chat_id=call.message.chat.id,
                              message_id=call.message.id)
        result = manage_events(users_input[call.from_user.id], call.from_user.id)

        if (isinstance(result, str)):
            bot.send_message(call.message.chat.id, result)
        else:
            bot.send_message(call.message.chat.id, construct_events(result), parse_mode="HTML")
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
        pass

def send_notifications(bot):
    while True:
        if not user_chat_id:
            time.sleep(10)
            continue

        for user_id, chat_id in user_chat_id.items():
            reminder = Reminder(get_user_credential(user_id))
            reminder.update()
            get_events_to_remind = reminder.get()
            print(get_events_to_remind)
            if (get_events_to_remind):
                bot.send_message(chat_id, construct_events(get_events_to_remind, "🔔Nadchodzące wydarzenia"), parse_mode="HTML")

        time.sleep(20)


if __name__ == "__main__":
    threading.Thread(target=send_notifications, args=(bot,), daemon=True).start()
    bot.infinity_polling()



