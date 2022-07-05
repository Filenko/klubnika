import os
import telebot
import psycopg2
from config import *
from flask import Flask, request
from datetime import datetime
from threading import Thread
import schedule
from time import sleep

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()

def add_pull_up(user_id, count):
    db_object.execute(f"UPDATE users SET pull_up = pull_up + {count} WHERE user_id = {user_id}")
    db_connection.commit()

def add_press(user_id, count):
    db_object.execute(f"UPDATE users SET press = press + {count} WHERE user_id = {user_id}")
    db_connection.commit()


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, f"Hello, {username}!")

    db_object.execute(f"SELECT user_id FROM users WHERE user_id = {user_id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users(user_id, username, pull_up, press, buffer_press, buffer_pull) VALUES (%s, %s, %s, %s, %s)", (user_id, username, 0, 0, 500, 500))
        db_connection.commit()
    else: 
        bot.reply_to(message, f"{result[0]}, {result[1]}, {result[2]}, {result[3]}, {result[4]}, {result[5]}!")        


@bot.message_handler(commands=["stats"])
def get_stats(message):
    db_object.execute("SELECT * FROM users ORDER BY pull_up")
    result = db_object.fetchall()

    if not result:
        bot.reply_to(message, "No data...")
    else:
        result = result[::-1]
        reply_message = "Топ:\n"
        for i, item in enumerate(result):
            flag = ''
            if item[2] >= 100 and item[3] >= 100:
                flag = '✅'
            reply_message += f"{flag}{i + 1}.{item[1].strip()} сделал {item[2]} анжуманя и {item[3]} прес\n"
        bot.reply_to(message, reply_message)

@bot.message_handler(commands=["buffer"])
def get_stats(message):
    db_object.execute("SELECT * FROM users ORDER BY pull_up")
    result = db_object.fetchall()

    if not result:
        bot.reply_to(message, "No data...")
    else:
        reply_message = "Буфер:\n"
        for i, item in enumerate(result):
            reply_message += f"У {item[1].strip()} осталось {item[5]} ажуманий и {item[4]} преСа\n"
        bot.reply_to(message, reply_message)


@bot.message_handler(commands=["me"])
def get_stats(message):
    db_object.execute(f"select * from users where user_id = {message.from_user.id}")
    result = db_object.fetchonea()

    if not result:
        bot.reply_to(message, "No data...")
    else:
        reply_message = ""
        reply_message += f"Сделал {result[2]} ажуманий и {result[3]} преСа\n"
        bot.reply_to(message, reply_message)

@bot.message_handler(commands=["pull_up"])
def get_stats(message):
    reply_message = message.text.split()
    if len(reply_message) == 1:
        add_pull_up (message.from_user.id, 10)
        bot.reply_to(message, f'Добавлено 10 анжуманя')    
    else:
        add_pull_up(message.from_user.id, reply_message[1])
        bot.reply_to(message, f'Добавлено {reply_message[1]} анжуманя')

@bot.message_handler(commands=["press"])
def get_stats(message):
    reply_message = message.text.split()
    if len(reply_message) == 1:
        add_press(message.from_user.id, 10)
        bot.reply_to(message, f'Добавлено 10 пресс')    
    else:
        add_press(message.from_user.id, reply_message[1])
        bot.reply_to(message, f'Добавлено {reply_message[1]} пресс')


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/index", methods=["HEAD", "GET"])
def index():
    return "!", 200


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def update_daily():
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    print(current_time)
    if current_time == "21:00":
        print(current_time)
        db_object.execute("""
            update Users set buffer_press = buffer_press - 100 + press
            where press < 100;
            update Users set buffer_pull = buffer_pull - 100 + pull_up
            where pull_up < 100;
            update Users set pull_up = 0, press = 0;
            """)
        db_connection.commit()
        



if __name__ == "__main__":

    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    #schedule.every(2).minutes.do(update_daily)
    # #schedule.every().day.at("05:28").do(update_daily)
    schedule.every(30).seconds.do(update_daily)
    Thread(target=schedule_checker).start() 
    #bot.infinity_polling()
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)))