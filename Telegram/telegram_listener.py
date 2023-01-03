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
sys.path.insert(1, os.path.join(sys.path[0], '..', 'NASA'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'News'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Weather'))
sys.path.insert(1, os.path.join(sys.path[0], '..', '..', 'Utilities'))

from telegram import Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import filters, ApplicationBuilder, CommandHandler, \
                            MessageHandler, ConversationHandler

import telegram_utils
import random_number_generator
import receive_todo_message_controller
import nasa
import news
import weather

import utils
import wait_for_internet

wait_for_internet.main()

telegram_ids, telegram_names = telegram_utils.get_users_info()
token = telegram_utils.get_token(sandbox = 'sandbox' in os.listdir())
bot = Bot(token)

def help_msg():
    '''Returns help message with list of commands'''
    commands = ['help - Available commands',
                'todo - Canvas todos',
                'weather - Local weather info',
                'news - Top 10 US news headlines',
                'nasa - NASA astronomy pic of the day',
                'rng - Random number generator',
                'clear - Clear screen']

    out = '<b><u>Supported commands:</u></b>\n'
    for command in commands:
        out += ' - /' + command + '\n'

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
            request_location=True)
        ]]
    )
    await telegram_utils.send_message(bot, user_id, ['Send location or /cancel'],
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


LOWER, UPPER, NUMS = range(3)

async def rng_start(update: Update, _):
    '''Initial function in /rng command pipeline, asks for lower bound'''
    user_id, _, _ = msg_info(update)
    await telegram_utils.send_message(bot, user_id, ['Enter lower bound or /cancel'])

    return LOWER

async def rng_lower(update: Update, context):
    '''Stores lower bound and asks for upper bound'''
    context.user_data['lower'] = update.message.text
    user_id, _, _ = msg_info(update)
    await telegram_utils.send_message(bot, user_id, ['Enter upper bound or /cancel'])

    return UPPER

async def rng_upper(update: Update, context):
    '''Stores upper bound and asks for nums'''
    context.user_data['upper'] = update.message.text
    user_id, _, _ = msg_info(update)
    await telegram_utils.send_message(bot, user_id, ['Enter number of values or /cancel'])

    return NUMS

async def rng_nums(update: Update, context):
    '''Calls main code to generate random numbers, clears stored data'''
    user_data = context.user_data
    lower = user_data['lower']
    upper = user_data['upper']
    nums = update.message.text

    out = random_number_generator.main([lower,upper,nums])

    user_data.clear()

    user_id = update.effective_chat.id
    await telegram_utils.send_message(bot, user_id, out)

    return ConversationHandler.END

async def rng_cancel(update: Update, context):
    '''/cancel command passed during /rng pipeline'''
    context.user_data.clear()
    user_id, _, _ = msg_info(update)
    await telegram_utils.send_message(bot, user_id, ["RNG command canceled"],
                                        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def rng_timeout(update: Update, context):
    '''/rng command timeout'''
    context.user_data.clear()
    user_id = update.effective_chat.id
    await telegram_utils.send_message(bot, user_id, ["RNG command timeout"],
                                        reply_markup=ReplyKeyboardRemove())


async def received_command(update:Update, _):
    '''General function for all received commands'''

    start = time.time()
    user_id, msg, approved = msg_info(update)

    cmd = msg.split()[0][1:]

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
            elif cmd == 'clear':
                out = '﹒'
                for _ in range(50):
                    out += '‎​\n'
                out = [out + '﹒']
            elif cmd == 'news':
                out = news.main()
            elif cmd == 'nasa':
                filename, title = nasa.main()
                if filename == None:
                    await telegram_utils.send_message(bot, user_id, ['No image today, sorry!'])
                else:
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
INTEGERS_REGEX = '^-?\\d+$'

if __name__ == '__main__':
    app = ApplicationBuilder().token(token).build()

    rng_handler = ConversationHandler(
        entry_points=[CommandHandler("rng", rng_start)],
        states={
            LOWER: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_lower)],
            UPPER: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_upper)],
            NUMS: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_nums)],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT | filters.COMMAND, \
                                            rng_timeout)],
        },
        fallbacks=[CommandHandler("cancel", rng_cancel)],
        conversation_timeout=CHAT_TIMEOUT
    )

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
    app.add_handler(rng_handler)
    app.add_handler(CommandHandler("start", received_command))
    app.add_handler(CommandHandler("help", received_command))
    app.add_handler(CommandHandler("ping", received_command))
    app.add_handler(CommandHandler("todo", received_command))
    app.add_handler(CommandHandler("clear", received_command))
    app.add_handler(CommandHandler("news", received_command))
    app.add_handler(CommandHandler("nasa", received_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command)) #unknown command
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message)) #any message

    app.run_polling()
