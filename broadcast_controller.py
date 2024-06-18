'''sends news / reminders broadcasts to relevant users'''

# pylint: disable=wrong-import-position

import os
import sys
import time
import datetime

from telegram import Bot
import canvasapi

import todos
import news
import jokes

# change working directory for run through cron
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from Utilities import wait_for_internet
from Utilities import general
from Utilities import key_manager
from Utilities import user_manager
from Utilities import telegram_utils

def main():
    '''driver code for sending broadcast'''

    wait_for_internet.main()

    start = time.time()
    print('--------------------------')
    print(datetime.datetime.now())
    print()

    if len(sys.argv) > 1:
        _user_manager = user_manager.UserManager(os.path.join('resources', 'user_info.json'))
        _key_manager = key_manager.KeyManager(os.path.join('resources', 'config.ini'))
        bot = Bot(_key_manager.get_telegram_key())

        broadcast_type = sys.argv[1]
        if broadcast_type == 'reminders':
            reminders_broadcast(_user_manager, bot)
        elif broadcast_type == 'news':
            news_broadcast(_user_manager, _key_manager, bot)
        elif broadcast_type == 'joke':
            joke_broadcast(_user_manager, bot)
        else:
            print('unrecognized broadcast type')
    else:
        print('no broadcast type argument')

    print(general.total_time(start))


def reminders_broadcast(_user_manager, bot):
    '''send reminders broadcast to all registered Canvas users'''

    if len(sys.argv) < 3:
        print('no reminders mode argument')
        return

    mode = sys.argv[2]

    if mode not in ('all', 'urgent'):
        print(f'unknown mode passed! - {mode}')
        return

    canvas_telegram_users = _user_manager.get_all_active_canvas_telegram_users()

    for user in canvas_telegram_users:
        name = user.name
        telegram_id = user.telegram_id

        print(f'Chat id: {telegram_id} ({name})')

        canvas_key = user.canvas_key
        canvas_url = user.canvas_url

        try:
            messages = todos.main(mode, canvas_key, canvas_url)
            telegram_utils.send_message_sync(bot, telegram_id, messages)
        except canvasapi.exceptions.CanvasException as ex:
            print(ex)


def news_broadcast(_user_manager, _key_manager, bot):
    '''send news broadcast to all Telegram users'''

    news_message = news.main(_key_manager.get_news_key())

    users = _user_manager.get_all_active_telegram_users()
    for user in users:
        print(f'Chat id: {user.telegram_id} ({user.name})')
        telegram_utils.send_message_sync(bot, user.telegram_id, news_message, \
                                         disable_web_page_preview=True)


def joke_broadcast(_user_manager, bot):
    '''send joke broadcast to all Telegram users'''

    joke = jokes.main()
    users = _user_manager.get_all_active_telegram_users()
    for user in users:
        print(f'Chat id: {user.telegram_id} ({user.name})')
        telegram_utils.send_message_sync(bot, user.telegram_id, joke, \
                                         disable_web_page_preview=True)


if __name__ == '__main__':
    main()
