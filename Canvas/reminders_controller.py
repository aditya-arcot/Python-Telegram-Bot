'''Send reminders to all users'''

import time
import datetime
import sys
import os

from telegram import Bot
import canvasapi

sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Telegram'))

import wait_for_internet
import todos
import canvas_utils
import telegram_utils
import utils

wait_for_internet.main()

start = time.time()
print('--------------------------')
print(datetime.datetime.now())
print()

canvas_names, keys = canvas_utils.get_canvas_users_info()
telegram_ids, telegram_names = telegram_utils.get_users_info()
bot = Bot(telegram_utils.get_token())

MODE = None
try:
    MODE = sys.argv[1]
except IndexError:
    print('no mode passed!')

if MODE is not None:
    if MODE not in ('all', 'urgent'):
        print(f'unknown mode passed! - {MODE}')
    else:
        for n, telegram_id in enumerate(telegram_ids):
            telegram_name = telegram_names[n]
            print(f'Chat id: {telegram_id} ({telegram_name})')

            if telegram_name in canvas_names:
                key = keys[canvas_names.index(telegram_name)]

                try:
                    messages = todos.main(MODE, key)
                    telegram_utils.send_message_sync(bot, telegram_id, messages)

                except canvasapi.exceptions.CanvasException as e:
                    print(e)

            else:
                print('Canvas todos not linked for this user!')

print(utils.total_time(start))
