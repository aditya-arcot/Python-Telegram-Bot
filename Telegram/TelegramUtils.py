import os, sys, time, asyncio
from matplotlib import lines
from telegram import Update, Bot

async def reply(update: Update, out: list):
    if len(out) > 0:
        print('Sending messages:')
        for i in out:
            print(i)
            await update.message.reply_text(i)
        print()

def new_message(bot: Bot, chat_id, out: list, parse_mode=None, disable_web_page_preview=None):
    if len(out) > 0:
        print('Sending messages:')
        for i in out:
            print(i)
            asyncio.get_event_loop().run_until_complete(
                bot.send_message(
                    chat_id=chat_id, text=i, parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview)
            )
        print()

def get_token(sandbox = False):
    path = os.path.join(sys.path[0], '..', 'Telegram', 'token.txt')
    f = open(path, "r")
    token = f.readlines()[1 if sandbox else 0].strip()
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
