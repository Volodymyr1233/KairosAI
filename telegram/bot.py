import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from AI.ai_handler import ai_parse_text
from utils import parse_json_to_bot_answer, manage_events, construct_events, generate_indexes, update_event
from Credentials.CredentialsFuntions_online import check_user_credentials, create_authorization_url, get_user_credential
from AI.event_schema import EventType
from GoogleAPI.GoogleCalendarAPI import deleteEvent, Reminder, getEvents
import time as t
import threading
from datetime import datetime, time
from zoneinfo import ZoneInfo

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

markup = InlineKeyboardMarkup(row_width=2)
markup.add(
    InlineKeyboardButton("Tak", callback_data='yes'),
    InlineKeyboardButton("Nie", callback_data='no')
)

users_input = {}

user_chat_id = {}




@bot.message_handler(commands=['start'])
def send_welcome(message):
    login_markup = InlineKeyboardMarkup()
    login_markup.add(InlineKeyboardButton("Login", url=create_authorization_url(message.from_user.id)))
    if check_user_credentials(message.from_user.id):
        bot.send_message(message.chat.id, "Cześć! Jak mogę ci dziś pomóc? 😊")
        if not message.from_user.id in user_chat_id:
            user_chat_id[message.from_user.id] = message.chat.id
    else:
        bot.send_message(message.chat.id,
                         "Hej! Wygląda na to, że nie jesteś zalogowany. Kliknij poniżej, aby się zalogować ⬇️",
                         reply_markup=login_markup)


@bot.message_handler(commands=['colors'])
def send_colors(message):
    bot.send_message(message.from_user.id, "Dostępne kolory dla wydarzeń to: \n🔵 jasnoniebieski\n🌿 miętowy\n💜 fioletowy\n🩷 łososiowy\n💛 żółty\n🟠 pomarańczowy\n🧵 turkusowy\n⚪ szary\n🔷 niebieski\n🌱 zielony\n🔴 czerwony")

@bot.message_handler(
    func=lambda mess: f"{mess.from_user.id}_generated_remove_indexes" in users_input and mess.text in users_input[
        f"{mess.from_user.id}_generated_remove_indexes"])
def send_remove_answer(message):
    if message.text == "Anuluj":
        bot.send_message(message.from_user.id, "Ewenty nie zostały usunięte", reply_markup=ReplyKeyboardRemove())
    else:
        try:
            remove_index = int(message.text) - 1
            deleteEvent(get_user_credential(message.from_user.id),
                        users_input[f"{message.from_user.id}_events_to_delete"][remove_index])
            bot.send_message(message.from_user.id, "Ewent został usunięty", reply_markup=ReplyKeyboardRemove())
        except Exception:
            bot.send_message(message.from_user.id, "Niestety usuwanie się nie powiodło ((")

    del users_input[f"{message.from_user.id}_events_to_delete"]
    del users_input[f"{message.from_user.id}_generated_remove_indexes"]
    del users_input[message.from_user.id]


@bot.message_handler(
    func=lambda mess: f"{mess.from_user.id}_generated_update_indexes" in users_input and mess.text in users_input[
        f"{mess.from_user.id}_generated_update_indexes"])
def send_update_answer(message):
    if (message.text == "Anuluj"):
        bot.send_message(message.from_user.id, "Żaden ewent nie został zaktualizowany!",
                         reply_markup=ReplyKeyboardRemove())
    else:
        try:
            update_index = int(message.text) - 1
            update_event(message.from_user.id, users_input[f"{message.from_user.id}_events_to_update"][update_index],
                         users_input[message.from_user.id])
            bot.send_message(message.from_user.id, "Ewent został zaktualizowany", reply_markup=ReplyKeyboardRemove())
        except ValueError:
            bot.send_message(message.from_user.id, "Podaj prosze i datę początkową i date końca. Napisz jeszcze raz porządnie")
        except Exception:
            bot.send_message(message.from_user.id, "Niestety nie udało się zaktualizować ewentu")
    del users_input[f"{message.from_user.id}_events_to_update"]
    del users_input[f"{message.from_user.id}_generated_update_indexes"]
    del users_input[message.from_user.id]


@bot.message_handler(content_types=['text'])
def send_command_message(message):
    login_markup = InlineKeyboardMarkup()
    login_markup.add(InlineKeyboardButton("Login", url=create_authorization_url(message.from_user.id)))
    if not check_user_credentials(message.from_user.id):
        bot.send_message(message.chat.id, "Ups! Nie mam jeszcze Twoich danych. Prosze się zaloguj...⬇️",
                         reply_markup=login_markup)
    else:
        if not message.from_user.id in user_chat_id:
            user_chat_id[message.from_user.id] = message.chat.id
        try:
            users_input[message.from_user.id] = ai_parse_text(message.text)
            bot_answer = parse_json_to_bot_answer(users_input[message.from_user.id])
            if bot_answer is not None:
                bot.send_message(message.chat.id,
                                 f"{bot_answer} \n\nDokładnie to ode mnie chcesz? Sprawdź czy wszystko się zgadza",
                                 reply_markup=markup, parse_mode='HTML')
            else:
                bot.send_message(message.chat.id, "Nie rozumiem. Proszę napisz dokładniej w czym mogę pomóc)")
        except Exception:
            bot.send_message(message.chat.id, "Niestety model AI jest przeciążony, spróbuj poźniej!")


@bot.callback_query_handler(func=lambda call: call.data in ["yes", "no"])
def send_callback(call):
    bot.answer_callback_query(call.id)
    if call.data == "yes":
        bot.edit_message_text("Okej już robię!", chat_id=call.message.chat.id,
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
            bot.send_message(call.message.chat.id, "Wybierz wydarzenie które chcesz zaktualizować",
                             reply_markup=update_markup)
    elif call.data == "no":
        bot.edit_message_text("Dobrze w takim razie napisz dokładnie co ty chcesz", chat_id=call.message.chat.id,
                              message_id=call.message.id)


def send_notifications(bot):
    reminders = {}
    while True:
        if not user_chat_id:
            t.sleep(10)
            continue

        for user_id, chat_id in user_chat_id.items():
            if not user_id in reminders:
                reminders[user_id] = Reminder(get_user_credential(user_id))

            get_events_to_remind = reminders[user_id].get()
            if (get_events_to_remind):
                bot.send_message(chat_id, construct_events(get_events_to_remind, f"🔔Nadchodzące wydarzenia"),
                                 parse_mode="HTML")

            reminders[user_id].update()

        t.sleep(20)


def send_notifications_for_day(bot):
    tz = ZoneInfo("Europe/Warsaw")
    while True:
        if not user_chat_id:
            t.sleep(10)
            continue
        date_now = datetime.now(tz)
        if (date_now >= datetime.combine(date_now.date(), time(6, 0), tzinfo=tz)):
            for user_id, chat_id in user_chat_id.items():
                events_for_today = getEvents(get_user_credential(user_id), time_min=date_now.isoformat(),
                                             time_max=datetime.combine(date_now.date(), time(23, 59),
                                                                       tzinfo=tz).isoformat())
                if (events_for_today):
                    bot.send_message(chat_id, construct_events(events_for_today, f"🔔Nadchodzące wydarzenia na dziś"),
                                     parse_mode="HTML")
            t.sleep(86400)  # sen na cały dzień (24 godz)
        else:
            t.sleep(15)


if __name__ == "__main__":
    threading.Thread(target=send_notifications, args=(bot,), daemon=True).start()
    threading.Thread(target=send_notifications_for_day, args=(bot,), daemon=True).start()
    bot.infinity_polling()
