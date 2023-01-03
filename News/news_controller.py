'''Send news headlines to all users'''

import os
import sys
import time
import datetime

from telegram import Bot

sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Telegram'))
sys.path.insert(1, os.path.join(sys.path[0], '..', '..', 'Utilities'))

import wait_for_internet
import utils

import telegram_utils
import news

wait_for_internet.main()

start = time.time()
print('--------------------------')
print(datetime.datetime.now())
print()

telegram_ids, telegram_names = telegram_utils.get_users_info()
bot = Bot(telegram_utils.get_token())

news_message = news.main()

for n, user_id in enumerate(telegram_ids):
    telegram_name = telegram_names[n]
    print(f'Chat id: {user_id} ({telegram_name})')

    telegram_utils.send_message_sync(bot, user_id, news_message, disable_web_page_preview=True)

print(utils.total_time(start))
