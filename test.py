import schedule
import telebot
from threading import Thread
from time import sleep
from flask import Flask, request
import os

TOKEN = "Some Token"

bot = telebot.TeleBot(TOKEN)
some_id = 12345 # This is our chat id.
server = Flask(__name__)

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def function_to_run():
    print("Hello, world!")


schedule.every(1).second.do(function_to_run)
print("Hello, world!")
schedule_checker() 