'''Telegram utility functions'''

import os
import sys
import asyncio
from telegram import Bot

def send_photo_sync(bot: Bot, chat_id, title, photo):
    '''Send photo from synchronous context'''

    asyncio.get_event_loop().run_until_complete(
        send_photo(
            bot, chat_id, title, photo
        )
    )

async def send_photo(bot: Bot, chat_id, title, photo):
    '''Send photo from asynchronous context'''

    print(f'Sending photo: {title}')
    print(photo)
    await bot.send_photo(chat_id, photo, caption=title)
    print()

def send_message_sync(bot: Bot, chat_id, out: list, parse_mode='HTML',
                        disable_web_page_preview=None, reply_markup=None):

    '''Send message from synchronous context'''

    asyncio.get_event_loop().run_until_complete(
        send_message(
            bot, chat_id, out, parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=reply_markup
        )
    )

async def send_message(bot: Bot, chat_id, out: list, parse_mode='HTML',
                        disable_web_page_preview=None, reply_markup=None):

    '''Send message from asynchronous context'''
    if out is not None:
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
    '''Read Telegram bot token from file'''

    path = os.path.join(sys.path[0], '..', 'Telegram', 'token.txt')
    token = ''
    with open(path, "r", encoding='ascii') as file:
        token = file.readlines()[1 if sandbox else 0].strip()
    return token

def get_users_info():
    '''Read Telegram user info from file'''

    path = os.path.join(sys.path[0], '..', 'Telegram', 'users.txt')

    ids, names = [], []
    with open(path, "r", encoding='ascii') as file:
        for line in file:
            lst = line.strip().split('\t')

            ids.append(int(lst[0]))
            names.append(lst[1])

    return ids, names
