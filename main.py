import telebot
from flask import Flask , render_template, jsonify, request, redirect, url_for, jsonify
import psycopg2
import os

bot = telebot.TeleBot("5208570240:AAGQmP5plGxVk8h8MSsRVy_d8gKhiRlaUXc")
app = Flask(__name__)

DB_URI = 'postgres://sxszeitvskatkt:252fcca6ea55cf02d40f2f9b8bbbe10d534d55b546b37764c37ad178a66ccfca@ec2-44-205-41-76.compute-1.amazonaws.com:5432/d9pu6bj42i81g3'
db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

    user_id = message.from_user.id
    username = tg_usr.username if tg_usr.username != None else '-' 
    bot.reply_to(message, f"Hello, {username}!")

    db_object.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = db_object.fetchone()

    if not result:
        db_object.execute("INSERT INTO users(user_id, username, pull_up, press) VALUES (%s, %s, %s, %s)", (user_id, username, 0, 0))
        db_connection.commit()
        bot.reply_to(message, f"Privet!")        

    


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

@app.route("/")
def home():
    bot.remove_webhook()
    bot.set_webhook(url='https://klubnika.herokuapp.com')
    return "1", 200

@app.route('/', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8443)))