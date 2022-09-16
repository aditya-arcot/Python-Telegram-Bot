import os, sys, time, asyncio
from matplotlib import lines
from telegram import Update, Bot

def send_photo_sync(bot: Bot, chat_id, title, url):
    asyncio.get_event_loop().run_until_complete(
        send_photo(
            bot, chat_id, title, url
        )
    )

async def send_photo(bot: Bot, chat_id, title, url):
    print('Sending photo: {}'.format(title))
    print(url)
    await bot.send_photo(chat_id, url, caption=title)
    print()

def send_message_sync(bot: Bot, chat_id, out: list, parse_mode='HTML', disable_web_page_preview=None, reply_markup=None):
    asyncio.get_event_loop().run_until_complete(
        send_message(
            bot, chat_id, out, parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup
        )
    )

async def send_message(bot: Bot, chat_id, out: list, parse_mode='HTML', disable_web_page_preview=None, reply_markup=None):
    if out != None:
        if len(out) > 0:
            print('Sending messages:')
            for i in out:
                print(i)
                await bot.send_message(
                    chat_id=chat_id, text=i,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                    reply_markup=reply_markup
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
