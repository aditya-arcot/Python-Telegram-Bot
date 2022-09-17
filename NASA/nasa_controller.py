'''Send NASA pic of the day to all users'''

import os
import sys
import time
import datetime

from telegram import Bot

sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Telegram'))

import wait_for_internet
import telegram_utils
import utils
import nasa

wait_for_internet.main()

start = time.time()
print('--------------------------')
print(datetime.datetime.now())
print()

telegram_ids, telegram_names = telegram_utils.get_users_info()
bot = Bot(telegram_utils.get_token())

filename, title = nasa.main()

for n, user_id in enumerate(telegram_ids):
    telegram_name = telegram_names[n]
    print(f'Chat id: {user_id} ({telegram_name})')

    with open(filename, 'rb') as image:
        telegram_utils.send_photo_sync(bot, user_id, title, image)

print(utils.total_time(start))
