import os
import telebot
import psycopg2
from config import *
from flask import Flask, request

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def add_pull_up(user_id, count):
    db_object.execute(f"UPDATE users SET pull_up = pull_up + count WHERE user_id = {user_id}")
    db_connection.commit()

def add_press(user_id, count):
    db_object.execute(f"UPDATE users SET pull_up = press + count WHERE user_id = {user_id}")
    db_connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, f"Hello, {username}!")

    db_object.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users(user_id, username, pull_up, press) VALUES (%s, %s, %s, %s)", (user_id, username, 0, 0))
        db_connection.commit()


@bot.message_handler(commands=["stats"])
def get_stats(message):
    db_object.execute("SELECT * FROM users ORDER BY pull_up")
    result = db_object.fetchall()

    if not result:
        bot.reply_to(message, "No data...")
    else:
        reply_message = "Top:\n"
        for i, item in enumerate(result):
            reply_message += f"{i + 1}. {item[1].strip()} has {item[2]} pulls_ups and {item[3]} press\n"
        bot.reply_to(message, reply_message)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def message_from_user(message):
    user_id = message.from_user.id
    update_messages_count(user_id)


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)))