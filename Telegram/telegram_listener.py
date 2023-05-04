'''Listener for Telegram messages sent to bot'''

import sys
import os
import datetime
import time

from telegram import Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (filters, ApplicationBuilder, CommandHandler,
                            MessageHandler, ConversationHandler, ContextTypes)

import telegram_utils

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import random_number_generator

sys.path.insert(1, os.path.join(sys.path[0], '..', 'Utilities'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Weather'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'News'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'NASA'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Canvas'))

import wait_for_internet
import key_manager
import user_manager
import general
import weather
import news
import nasa
import todos

def help_msg():
    '''Returns help message with list of commands'''
    commands = ['help - Available commands',
                'todo - Canvas todos',
                'weather - Local weather info',
                'news - Top 10 US news headlines',
                'nasa - NASA astronomy pic of the day',
                'rng - Random number generator']

    out = '<b><u>Supported commands:</u></b>\n'
    for command in commands:
        out += ' - /' + command + '\n'

    return [out]

def handle_update(update, text=True):
    '''Returns user for received message'''
    telegram_id = update.effective_chat.id
    msg = update.message.text.lower() if text else 'non_text_msg'

    print('--------------------------')
    print(datetime.datetime.now())
    print()

    print('Message received')
    print(f'Chat id: {telegram_id}')
    print(f'Message: {msg}')
    print()

    user = _user_manager.get_user_from_telegram_id(telegram_id)

    if user is None:
        print('Unapproved sender')
        print()
        return False

    print(f'Approved sender: {user.name}')
    print()
    return True


LOCATION = 0

async def weather_start(update: Update, context) -> int:
    '''Initial function in /weather command pipeline'''
    context.user_data['weather_start'] = time.time()
    if not handle_update(update): # only need to check approval in 1st message of pipeline
        await telegram_utils.send_message(bot, update.effective_chat.id, ['Unauthorized'])
        return

    # don't use 1 time keyboard
    # location not sent after clicking button on desktop
    reply_markup=ReplyKeyboardMarkup(
        [[KeyboardButton(
            text="Send Location",
            request_location=True)
        ]]
    )
    await telegram_utils.send_message(bot, update.effective_chat.id, ['Send location or /cancel'],
                                        reply_markup=reply_markup)
    return LOCATION

async def weather_main(update: Update, context) -> int:
    '''Gets weather info after location is passed'''
    handle_update(update, text=False)

    loc = update.message.location
    lat, lng = loc['latitude'], loc['longitude']
    out = weather.main(lat, lng, _key_manager.get_weather_key())

    await telegram_utils.send_message(bot, update.effective_chat.id, out, reply_markup=ReplyKeyboardRemove())
    return end_weather_pipeline(context)

async def weather_cancel(update: Update, context) -> int:
    '''/cancel command passed during /weather pipeline'''
    handle_update(update)
    await telegram_utils.send_message(bot, update.effective_chat.id, ["Weather command canceled"],
                                        reply_markup=ReplyKeyboardRemove())
    return end_weather_pipeline(context)

async def weather_timeout(update, context):
    '''/weather command timeout'''
    await telegram_utils.send_message(bot, update.effective_chat.id, ["Weather command timeout"],
                                        reply_markup=ReplyKeyboardRemove())
    return end_weather_pipeline(context)

def end_weather_pipeline(context):
    '''end weather conversation actions'''
    print(general.total_time(context.user_data.pop('weather_start')))
    return ConversationHandler.END


LOWER, UPPER, NUMS = range(3)

async def rng_start(update: Update, context):
    '''Initial function in /rng command pipeline, asks for lower bound'''
    context.user_data['rng_start'] = time.time()
    if not handle_update(update): # only need to check approval in 1st message of pipeline
        await telegram_utils.send_message(bot, update.effective_chat.id, ['Unauthorized'])
        return

    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ['Enter lower bound or /cancel'])
    return LOWER

async def rng_lower(update: Update, context):
    '''Stores lower bound and asks for upper bound'''
    context.user_data['lower'] = update.message.text
    handle_update(update)
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ['Enter upper bound or /cancel'])
    return UPPER

async def rng_upper(update: Update, context):
    '''Stores upper bound and asks for nums'''
    context.user_data['upper'] = update.message.text
    handle_update(update)
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ['Enter number of values or /cancel'])
    return NUMS

async def rng_nums(update: Update, context):
    '''Calls main code to generate random numbers, clears stored data'''
    handle_update(update)

    user_data = context.user_data
    lower = user_data['lower']
    upper = user_data['upper']
    nums = update.message.text

    out = random_number_generator.main([lower,upper,nums])

    await telegram_utils.send_message(bot, update.effective_chat.id, out)
    return end_rng_pipeline(context)

async def rng_cancel(update: Update, context):
    '''/cancel command passed during /rng pipeline'''
    handle_update(update)
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ["RNG command canceled"])
    return end_rng_pipeline(context)

async def rng_timeout(update: Update, context):
    '''/rng command timeout'''
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ["RNG command timeout"])
    return end_rng_pipeline(context)

def end_rng_pipeline(context):
    '''end rng conversation actions'''
    user_data = context.user_data
    user_data.pop('lower')
    user_data.pop('upper')
    print(general.total_time(user_data.pop('rng_start')))
    return ConversationHandler.END


async def received_command(update:Update, _):
    '''General function for all received commands'''

    start = time.time()
    approved = handle_update(update)
    cmd = update.message.text.lower().split()[0][1:]
    out = []

    if cmd == 'start':
        out = ['<b>Welcome!</b>']
        if not approved:
            out.append(f'Contact admin for approval!\nProvide id # {update.effective_chat.id}')

        else:
            out += help_msg()

    else:
        if approved:
            if cmd == 'help':
                out = help_msg()

            elif cmd == 'ping':
                out = ['pong']

            elif cmd == 'todo':
                user = _user_manager.get_user_from_telegram_id(update.effective_chat.id)
                if user.canvas_status == 'inactive':
                    await telegram_utils.send_message(bot, update.effective_chat.id,
                            ['Not registered for Canvas todos. Contact admin!'])

                else:
                    messages = todos.main('all', user.canvas_key, user.canvas_url)
                    await telegram_utils.send_message(bot, update.effective_chat.id, messages)

            elif cmd == 'news':
                out = news.main(_key_manager.get_news_key())

            elif cmd == 'nasa':
                filename, title = nasa.main(_key_manager.get_nasa_key())
                if filename is None:
                    await telegram_utils.send_message(bot, update.effective_chat.id,
                                                      ['No image today!'])

                else:
                    with open(filename, 'rb') as image:
                        await telegram_utils.send_photo(bot, update.effective_chat.id, title, image)

            else:
                print(f'unknown cmd provided - {cmd} - check code')

        else:
            out = ['Unauthorized']

    if cmd != 'nasa':
        await telegram_utils.send_message(bot, update.effective_chat.id, out,
                                          disable_web_page_preview=True
                                          if cmd=='news' else None)
    print(general.total_time(start))

async def unknown_command(update: Update, _):
    '''Received unrecognized command'''

    start = time.time()
    if handle_update(update):
        await telegram_utils.send_message(bot, update.effective_chat.id,
                                          ['Command not recognized'] + help_msg())
    else:
        await telegram_utils.send_message(bot, update.effective_chat.id, ['Unauthorized'])
    print(general.total_time(start))

async def message(update: Update, _):
    '''Received message, not command'''

    start = time.time()
    if handle_update(update):
        await telegram_utils.send_message(bot, update.effective_chat.id,
                                          [r'Please enter a command (starting with \)']
                                            + help_msg())
    else:
        await telegram_utils.send_message(bot, update.effective_chat.id, ['Unauthorized'])
    print(general.total_time(start))

CHAT_TIMEOUT = 30
INTEGERS_REGEX = '^-?\\d+$'

if __name__ == '__main__':
    wait_for_internet.main()

    _user_manager = user_manager.UserManager(os.path.join(sys.path[0], '..', 'secrets',
                                                            'user_info.json'))

    _key_manager = key_manager.KeyManager(os.path.join(sys.path[0], '..', 'secrets', 'config.ini'))
    bot = Bot(_key_manager.get_telegram_key())
    app = ApplicationBuilder().token(_key_manager.get_telegram_key()).build()

    rng_handler = ConversationHandler(
        entry_points=[CommandHandler("rng", rng_start)],
        states={
            LOWER: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_lower)],
            UPPER: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_upper)],
            NUMS: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_nums)],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT | filters.COMMAND,
                                            rng_timeout)]
        },
        fallbacks=[CommandHandler("cancel", rng_cancel)],
        conversation_timeout=CHAT_TIMEOUT
    )
    app.add_handler(rng_handler)

    weather_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_start)],
        states={
            LOCATION: [MessageHandler(filters.LOCATION, weather_main)],
            ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT | filters.COMMAND,
                                            weather_timeout)]
        },
        fallbacks=[CommandHandler("cancel", weather_cancel)],
        conversation_timeout=CHAT_TIMEOUT
    )
    app.add_handler(weather_handler)

    app.add_handler(CommandHandler("start", received_command))
    app.add_handler(CommandHandler("help", received_command))
    app.add_handler(CommandHandler("ping", received_command))
    app.add_handler(CommandHandler("todo", received_command))
    app.add_handler(CommandHandler("news", received_command))
    app.add_handler(CommandHandler("nasa", received_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))

    app.run_polling()
