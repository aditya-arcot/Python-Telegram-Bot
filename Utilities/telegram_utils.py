'''Telegram utility functions'''

import asyncio
import warnings

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
from telegram import Bot

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

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
                print(BeautifulSoup(i.strip(), "html.parser").get_text())
                await bot.send_message(
                    chat_id=chat_id, text=i,
                    parse_mode=parse_mode,
                    disable_web_page_preview=disable_web_page_preview,
                    reply_markup=reply_markup
                )
            print()
