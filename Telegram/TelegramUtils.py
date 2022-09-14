import os
from matplotlib import lines
from telegram import Update, Bot
import sys
import time

async def reply(update: Update, out: list):
    if len(out) > 0:
        print('Sending messages:')
        for i in out:
            print(i)
            await update.message.reply_text(i)
        print()

def new_message(bot: Bot, chat_id, out: list):
    if len(out) > 0:
        print('Sending messages:')
        for i in out:
            print(i)
            asyncio.get_event_loop().run_until_complete(bot.send_message(chat_id=chat_id, text=i))
        print()

def get_token():
    path = os.path.join(sys.path[0], '..', 'Telegram', 'token.txt')
    f = open(path, "r")
    token = f.readlines()[0].strip() #change to 1 for sandbox bot
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
