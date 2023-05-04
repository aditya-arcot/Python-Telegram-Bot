'''Send reminders to all users'''

import time
import datetime
import sys
import os

from telegram import Bot
import canvasapi

import todos

sys.path.insert(1, os.path.join(sys.path[0], '..', 'Utilities'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Telegram'))

import wait_for_internet
import general
import key_manager
import user_manager
import telegram_utils

def main():
    '''driver for urgent / all reminders'''

    wait_for_internet.main()

    start = time.time()
    print('--------------------------')
    print(datetime.datetime.now())
    print()

    try:
        mode = sys.argv[1]
    except IndexError:
        print('no mode passed!')
        print(general.total_time(start))
        return

    if mode not in ('all', 'urgent'):
        print(f'unknown mode passed! - {mode}')
        print(general.total_time(start))
        return

    _key_manager = key_manager.KeyManager(os.path.join(sys.path[0], '..', 'secrets', 'config.ini'))
    bot = Bot(_key_manager.get_telegram_key())

    _user_manager = user_manager.UserManager(os.path.join(sys.path[0], '..', 'secrets', \
                                                            'user_info.json'))
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

    print(general.total_time(start))

if __name__ == '__main__':
    main()
