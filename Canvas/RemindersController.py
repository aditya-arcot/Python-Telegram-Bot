import time, datetime, sys, os
import asyncio

# add parent dir
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import WaitForInternet
WaitForInternet.main()

from telegram import Bot

# add Telegram dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Telegram'))

import Todos
import CanvasUtils
import TelegramUtils
import Utils

start = time.time()
print('--------------------------')
print(datetime.datetime.now())
print()

canvas_names, keys = CanvasUtils.get_canvas_users_info()
ids, telegram_names = TelegramUtils.get_users_info()
bot = Bot(TelegramUtils.get_token())

mode = None
try:
    mode = sys.argv[1]
except Exception as e:
    print('no mode passed!')

if mode != None:
    if mode != 'all' and mode != 'urgent':
        print('unknown mode passed! - {}'.format(mode))
    else:
        for i in range(len(ids)):
            id = ids[i]
            telegram_name = telegram_names[i]
            print('Chat id: {} ({})'.format(id, telegram_name))

            if telegram_name in canvas_names:
                key = keys[canvas_names.index(telegram_name)]

                messages = Todos.main(mode, key)
                TelegramUtils.new_message(bot, id, messages)

            else:
                print('Canvas todos not linked for this user!')

print(Utils.total_time(start))
