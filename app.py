import threading


from telegram.bot import bot, send_notifications, send_notifications_for_day


if __name__ == "__main__":
    threading.Thread(target=send_notifications, args=(bot,), daemon=True).start()
    threading.Thread(target=send_notifications_for_day, args=(bot,), daemon=True).start()
    bot.infinity_polling()