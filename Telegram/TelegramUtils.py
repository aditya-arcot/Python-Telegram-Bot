import os
from matplotlib import lines
from telegram import Update, Bot
import sys
import time

def send_reply_messages(update: Update, messages: list):
    print('Sending messages:')
    for i in messages:
        print(i)
        update.message.reply_text(i)
    print()

def send_new_messages(bot: Bot, chat_id, messages: list):
    print('Sending messages:')
    for i in messages:
        print(i)
        bot.send_message(text=i, chat_id=chat_id)
    print()

def get_token():
    path = os.path.join(sys.path[0], '..', 'Telegram', 'token.txt')
    f = open(path, "r")
    token = f.readlines()[0].strip()
    f.close()
    return token

def get_users_info():
    path = os.path.join(sys.path[0], '..', 'Telegram', 'users.txt')
    f = open(path, "r")

    ids, names = [], []
    for line in f:
        lst = line.strip().split('\t')
        
        ids.append(int(lst[0]))
        names.append(lst[1])

    f.close()

    return ids, names
