'''Listener for Telegram messages sent to bot'''

import logging
import sys
import os
import datetime
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)

sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Canvas'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Weather'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'News'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'NASA'))

from telegram import Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import filters, ApplicationBuilder, CommandHandler, \
                            MessageHandler, ConversationHandler

import utils
import random_number_generator
import telegram_utils
import wait_for_internet
import receive_todo_message_controller
import weather
import news
import nasa

wait_for_internet.main()

telegram_ids, telegram_names = telegram_utils.get_users_info()
token = telegram_utils.get_token(sandbox=True)
bot = Bot(token)

def help_msg():
    '''Returns help message with list of commands'''
    out = '<b><u>Supported commands:</u></b>\n'
    out += ' - /help\n'
    out += ' - /todo\n'
    out += ' - /weather\n'
    out += ' - /news\n'
    out += ' - /rng min max [n]\n'
    out += ' - /nasa\n'
    out += ' - /clear'
    return [out]

def msg_info(update, text=True):
    '''Returns info about received message'''
    user_id = update.effective_chat.id
    msg = update.message.text.lower() if text else 'non_text_msg'

    print('--------------------------')
    print(datetime.datetime.now())
    print()

    print('Message received')
    print(f'Chat id: {user_id}')
    print(f'Message: {msg}')
    print()

    if user_id not in telegram_ids:
        print('Unapproved sender')
        print()
        return user_id, msg, False

    name = telegram_names[telegram_ids.index(user_id)]
    print(f'Approved sender: {name}')
    print()
    return user_id, msg, True


LOCATION = 0

async def weather_start(update: Update, _) -> int:
    '''Initial function in /weather command pipeline'''
    user_id, _, _ = msg_info(update)
    reply_markup=ReplyKeyboardMarkup(
        [[KeyboardButton(
            text="Send Location",
            request_location=True,
            one_time_keyboard=True)
        ]]
    )
    await telegram_utils.send_message(bot, user_id, ['Send location below or press /cancel'],
                                        reply_markup=reply_markup)

    return LOCATION

async def weather_main(update: Update, _) -> int:
    '''Gets weather info after location is passed'''
    user_id, _, _ = msg_info(update, text=False)
    loc = update.message.location
    lat, lng = loc['latitude'], loc['longitude']
    out = weather.main(lat, lng)
    reply_markup=ReplyKeyboardRemove()
    await telegram_utils.send_message(bot, user_id, out, reply_markup=reply_markup)

    return ConversationHandler.END

async def weather_cancel(update: Update, _) -> int:
    '''/cancel command passed during /weather pipeline'''
    user_id, _, _ = msg_info(update)
    await telegram_utils.send_message(bot, user_id, ["Weather command canceled"],
                                        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def weather_timeout(update, _):
    '''/weather command timeout'''
    user_id = update.effective_chat.id
    await telegram_utils.send_message(bot, user_id, ["Weather command timeout"],
                                        reply_markup=ReplyKeyboardRemove())


async def received_command(update:Update, _):
    '''General function for all received commands'''

    start = time.time()
    user_id, msg, approved = msg_info(update)

    msg_lst = msg.split()
    cmd = msg_lst[0][1:]
    args = msg_lst[1:]

    out = []
    if cmd == 'start':
        out = ['<b>Welcome!</b>']
        if not approved:
            out.append(f'Contact admin for approval!\nProvide id # {user_id}')
        else:
            out += help_msg()
    else:
        if approved:
            if cmd == 'help':
                out = help_msg()
            elif cmd == 'ping':
                out = ['pong']
            elif cmd == 'todo':
                out = receive_todo_message_controller.main(
                        telegram_names[telegram_ids.index(user_id)])
                if out == []:
                    out = ['You are not registered for Canvas todos. Contact admin!']
            elif cmd == 'rng':
                out = random_number_generator.main(args)
            elif cmd == 'clear':
                out = ''
                for _ in range(50):
                    out += '﹒\n'
                out = [out]
            elif cmd == 'news':
                out = news.main()
            elif cmd == 'nasa':
                filename, title = nasa.main()
                with open(filename, 'rb') as image:
                    await telegram_utils.send_photo(bot, user_id, title, image)
            else:
                print(f'unknown cmd provided - {cmd} - check code')
        else:
            out = ['Unauthorized']

    if cmd != 'nasa':
        await telegram_utils.send_message(bot, user_id, out, disable_web_page_preview=True \
                                        if cmd=='news' else None)
    print(utils.total_time(start))

async def unknown_command(update: Update, _):
    '''Received unrecognized command'''

    start = time.time()
    user_id, _, approved = msg_info(update)
    if approved:
        await telegram_utils.send_message(bot, user_id, ['Command not recognized'] + help_msg())
    else:
        await telegram_utils.send_message(bot, user_id, ['Unauthorized'])
    print(utils.total_time(start))

async def message(update: Update, _):
    '''Received message, not command'''

    start = time.time()
    user_id, _, approved = msg_info(update)
    if approved:
        await telegram_utils.send_message(bot, user_id, ['Please use commands, not messages'] \
                                                    + help_msg())
    else:
        await telegram_utils.send_message(bot, user_id, ['Unauthorized'])
    print(utils.total_time(start))

CHAT_TIMEOUT = 30

if __name__ == '__main__':
    app = ApplicationBuilder().token(token).build()

    weather_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_start)],
            states={
                LOCATION: [
                    MessageHandler(filters.LOCATION, weather_main),
                ],
                ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT | filters.COMMAND, \
                                                weather_timeout)],
            },
            fallbacks=[CommandHandler("cancel", weather_cancel)],
            conversation_timeout=CHAT_TIMEOUT
    )

    app.add_handler(weather_handler)
    app.add_handler(CommandHandler("start", received_command))
    app.add_handler(CommandHandler("help", received_command))
    app.add_handler(CommandHandler("ping", received_command))
    app.add_handler(CommandHandler("todo", received_command))
    app.add_handler(CommandHandler("rng", received_command))
    app.add_handler(CommandHandler("clear", received_command))
    app.add_handler(CommandHandler("news", received_command))
    app.add_handler(CommandHandler("nasa", received_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command)) #unknown command
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message)) #any message

    app.run_polling()
