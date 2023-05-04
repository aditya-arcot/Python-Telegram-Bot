'''Send news headlines to all users'''

import os
import time
import datetime

from telegram import Bot

import news

from Utilities import wait_for_internet
from Utilities import general
from Utilities import key_manager
from Utilities import user_manager
from Utilities import telegram_utils

def main():
    '''driver for news messages'''

    wait_for_internet.main()

    start = time.time()
    print('--------------------------')
    print(datetime.datetime.now())
    print()

    _key_manager = key_manager.KeyManager(os.path.join('resources', 'config.ini'))
    bot = Bot(_key_manager.get_telegram_key())

    news_message = news.main(_key_manager.get_news_key())

    _user_manager = user_manager.UserManager(os.path.join('resources', 'user_info.json'))
    users = _user_manager.get_all_active_telegram_users()
    for user in users:
        print(f'Chat id: {user.telegram_id} ({user.name})')
        telegram_utils.send_message_sync(bot, user.telegram_id, news_message, \
                                         disable_web_page_preview=True)

    print(general.total_time(start))

if __name__ == '__main__':
    main()
