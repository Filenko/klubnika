import telebot
from flask import Flask , render_template, jsonify, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os

bot = telebot.TeleBot("5208570240:AAGQmP5plGxVk8h8MSsRVy_d8gKhiRlaUXc")
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://esftupvernqgde:d4580dafa8a9d85ff2fa1627d3a91c2da447f4945c84a3f48bf291a7856a2b36@ec2-23-23-151-191.compute-1.amazonaws.com:5432/d934qinsg9rah8'
db = SQLAlchemy(app)

class User(db.Model):

    _id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    pull_up = db.Column(db.Integer)
    press = db.Column(db.Integer)


    def __init__(self, user_idd, press, pull_up, name):
        self.user_id = user_idd
        self.press = press
        self.pull_up = pull_up


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):

    usr = User.query.filter_by(user_id = message.from_user.id).first()
    tg_usr = message.from_user

    if usr is None:
        first = tg_usr.first_name if tg_usr.first_name != None else '-' 
        user_id = message.from_user.id
        new_data = User(user_id, 0, 0)
        db.session.add(new_data)
        bot.send_message(message.chat.id, f'Привет! Вы добавлены в базу, {first}!')
    db.session.commit()


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