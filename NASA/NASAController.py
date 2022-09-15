import os, sys, time, datetime, asyncio

# add parent dir
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import WaitForInternet
WaitForInternet.main()

from telegram import Bot

# add Telegram dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Telegram'))

import TelegramUtils
import Utils
import NASA

start = time.time()
print('--------------------------')
print(datetime.datetime.now())
print()

ids, telegram_names = TelegramUtils.get_users_info()
bot = Bot(TelegramUtils.get_token())

url, title = NASA.main()

for i in range(len(ids)):
    id = ids[i]
    telegram_name = telegram_names[i]
    print('Chat id: {} ({})'.format(id, telegram_name))

    TelegramUtils.send_photo_sync(bot, id, title, url)

print(Utils.total_time(start))
