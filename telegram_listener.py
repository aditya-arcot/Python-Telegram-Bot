'''Listener for Telegram messages sent to bot'''

# pylint: disable=wrong-import-position

import os
import sys
import datetime
import time

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.error import NetworkError
from telegram.ext import (filters, ApplicationBuilder, CommandHandler, PicklePersistence,
                            MessageHandler, ConversationHandler, ContextTypes, PersistenceInput)

import random_number_generator
import weather
import news
import nasa
import todos
import jokes

# change working directory for run through cron
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from Utilities import telegram_utils
from Utilities import wait_for_internet
from Utilities import key_manager
from Utilities import user_manager
from Utilities import general
from Utilities import timer_utils

def help_msg():
    '''Returns help message with list of commands'''
    commands = ['<b><u>Supported commands:</u></b>',
                '/help - Available commands',
                '/todo - Canvas todos',
                '/joke - Random joke',
                '/weather - Local weather info',
                '/news - Top 10 US news headlines',
                '/nasa - NASA astronomy pic of the day',
                '/random - Random number generator',
                '/timer - Custom timers']
    return commands

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


MODE, REMOVE, NAME, UNIT, DURATION = range(5)

async def timer_init(_):
    '''Initializes job queue with existing timers'''

    if not app.bot_data.get('timers'):
        app.bot_data['timers'] = {}
        return

    for chat_id in app.bot_data['timers']:
        for timer in app.bot_data['timers'][chat_id].values():
            if timer.remaining_seconds() < 0:
                app.job_queue.run_once(timer_alarm, 0, chat_id=chat_id,
                                    data={'timer':timer, 'expired':True})
            else:
                app.job_queue.run_once(timer_alarm, timer.duration, chat_id=chat_id,
                                    data={'timer':timer,})

async def timer_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Initial function in /timer command pipeline'''

    context.user_data['timer_start'] = time.time()
    if not handle_update(update): # only need to check approval in 1st message of pipeline
        await telegram_utils.send_message(bot, update.effective_chat.id, ['Unauthorized'])
        return

    reply_markup = ReplyKeyboardMarkup([["Add", "Remove", "List"]], one_time_keyboard=True)

    await telegram_utils.send_message(bot, update.effective_chat.id, ['Enter mode or /cancel'],
                                      reply_markup=reply_markup)
    return MODE

async def timer_add(update: Update, _) -> int:
    '''Gets new timer name'''

    handle_update(update)

    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ['Enter a name for the timer or /cancel'],
                                      reply_markup=ReplyKeyboardRemove())
    return NAME

async def timer_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Gets new timer time unit after saving name'''

    handle_update(update)

    context.user_data['name'] = update.message.text

    reply_markup = ReplyKeyboardMarkup([["Days", "Hours", "Minutes", "Seconds"]],
                                       one_time_keyboard=True)
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ['Choose a time unit or /cancel'],
                                      reply_markup=reply_markup)
    return UNIT

async def timer_unit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Gets new timer duration after saving time unit'''

    handle_update(update)

    context.user_data['unit'] = update.message.text[0]

    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ['Enter an integer duration or /cancel'],
                                      reply_markup=ReplyKeyboardRemove())

    return DURATION

async def timer_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Creates timer after saving duration'''

    handle_update(update)

    name = context.user_data['name']
    unit = context.user_data['unit']
    duration = int(update.message.text)
    chat_id = update.effective_chat.id

    if unit == 'D':
        duration *= 60 * 60 * 24
    elif unit == 'H':
        duration *= 60 * 60
    elif unit == 'M':
        duration *= 60

    curr_time = int(time.time())
    timer = timer_utils.Timer(name, chat_id, curr_time, duration)

    if not app.bot_data['timers'].get(chat_id):
        app.bot_data['timers'][chat_id] = {}
    app.bot_data['timers'][chat_id][curr_time] = timer

    context.job_queue.run_once(timer_alarm, duration, chat_id=chat_id,
                               data={'timer': timer})

    await telegram_utils.send_message(bot, chat_id, ['Timer successfully created'],
                                      reply_markup=ReplyKeyboardRemove())

    return end_timer_pipeline(context)

async def timer_remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Gets timer to remove'''

    handle_update(update)

    if len(context.job_queue.jobs()) == 0:
        await telegram_utils.send_message(bot, update.effective_chat.id,
                                          ['No active timers'],
                                          reply_markup=ReplyKeyboardRemove())
        return end_timer_pipeline(context)

    messages = ['<b><u>Make a selection:</u></b>']
    for i, job in enumerate(context.job_queue.jobs()):
        timer = job.data['timer']
        messages.append(f'{i} - {timer}')
    await telegram_utils.send_message(bot, update.effective_chat.id, messages,
                                      reply_markup=ReplyKeyboardRemove())

    return REMOVE

async def timer_remove_core(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Removes timer from existing'''

    handle_update(update)

    selection = int(update.message.text)

    if selection < 0 or selection >= len(context.job_queue.jobs()):
        await telegram_utils.send_message(bot, update.effective_chat.id,
                                          ['Invalid selection, try again or /cancel'],
                                          reply_markup=ReplyKeyboardRemove())
        return REMOVE

    timer = context.job_queue.jobs()[selection].data['timer']
    chat_id = timer.chat_id

    context.job_queue.jobs()[selection].schedule_removal()
    app.bot_data['timers'][chat_id].pop(timer.start)

    await telegram_utils.send_message(bot, update.effective_chat.id,
                                        ['Timer removed'],
                                        reply_markup=ReplyKeyboardRemove())

    return end_timer_pipeline(context)

async def timer_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Lists existing timers'''

    handle_update(update)

    if len(context.job_queue.jobs()) == 0:
        await telegram_utils.send_message(bot, update.effective_chat.id,
                                          ['No active timers'],
                                          reply_markup=ReplyKeyboardRemove())
        return end_timer_pipeline(context)

    messages = ['<b><u>Active timers:</u></b>']
    for job in context.job_queue.jobs():
        timer = job.data['timer']
        messages.append(f'{timer}')
    await telegram_utils.send_message(bot, update.effective_chat.id, messages,
                                      reply_markup=ReplyKeyboardRemove())

    return end_timer_pipeline(context)

async def timer_alarm(context: ContextTypes.DEFAULT_TYPE):
    '''Displays message when timer expires'''

    job = context.job
    timer = job.data['timer']

    chat_id = timer.chat_id
    app.bot_data['timers'][chat_id].pop(timer.start)

    if job.data.get('expired'):
        await telegram_utils.send_message(bot, job.chat_id,
                                          ["<b><u>Alarm rang while bot was down!</u></b> -" +
                                           f"{timer.name}"])
    else:
        await telegram_utils.send_message(bot, job.chat_id,
                                          [f"<b><u>Timer alarm!</u></b> - {timer.name}"])

async def timer_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''/cancel entered during /timer pipeline'''
    handle_update(update)
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ["Timer command canceled"],
                                        reply_markup=ReplyKeyboardRemove())
    return end_timer_pipeline(context)

async def timer_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    '''Timeout during /timer pipeline'''
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ["Timer command timeout"],
                                        reply_markup=ReplyKeyboardRemove())
    return end_timer_pipeline(context)

def end_timer_pipeline(context):
    '''Ends timer conversation actions'''
    context.user_data.pop('name', None)
    context.user_data.pop('unit', None)
    print(general.total_time(context.user_data.pop('timer_start')))
    return ConversationHandler.END


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

    await telegram_utils.send_message(bot, update.effective_chat.id, out,
                                        reply_markup=ReplyKeyboardRemove())
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
    '''End weather conversation actions'''
    print(general.total_time(context.user_data.pop('weather_start')))
    return ConversationHandler.END


LOWER, UPPER, NUMS = range(3)

async def rng_start(update: Update, context):
    '''Initial function in /random command pipeline, asks for lower bound'''
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
    '''/cancel command passed during /random pipeline'''
    handle_update(update)
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ["RNG command canceled"])
    return end_rng_pipeline(context)

async def rng_timeout(update: Update, context):
    '''/random command timeout'''
    await telegram_utils.send_message(bot, update.effective_chat.id,
                                      ["RNG command timeout"])
    return end_rng_pipeline(context)

def end_rng_pipeline(context):
    '''Ends rng conversation actions'''
    user_data = context.user_data
    user_data.pop('lower', None)
    user_data.pop('upper', None)
    print(general.total_time(user_data.pop('rng_start')))
    return ConversationHandler.END


async def received_command(update:Update, _):
    '''General function for all received commands'''

    # pylint: disable=too-many-branches

    start = time.time()
    approved = handle_update(update)
    cmd = update.message.text.lower().split()[0][1:]
    out = []

    if cmd == 'start':
        out = ['<b>Welcome!</b>']
        if not approved:
            out.append('Contact admin for approval!')
            out.append(f'Provide id # {update.effective_chat.id}')

        else:
            out += help_msg()

    else:
        if approved:
            if cmd == 'help':
                out = help_msg()

            elif cmd == 'status':
                out = ['Online']

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

            elif cmd == 'joke':
                out = jokes.main()

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
INTEGERS_REGEX = r'^-?\d+$'

if __name__ == '__main__':
    print(datetime.datetime.now())
    wait_for_internet.main()

    _user_manager = user_manager.UserManager(os.path.join('resources', 'user_info.json'))
    _key_manager = key_manager.KeyManager(os.path.join('resources', 'config.ini'))

    persistence = PicklePersistence(store_data=PersistenceInput(bot_data=True),
                                    filepath=os.path.join('resources', 'telegram_bot.pickle'))
    app = ApplicationBuilder().token(_key_manager.get_telegram_key()).post_init(timer_init)\
                                .persistence(persistence).build()
    bot = app.bot

    timer_handler = ConversationHandler(
        entry_points=[CommandHandler("timer", timer_start)],
        states={
            MODE: [MessageHandler(filters.TEXT & (~ filters.COMMAND) & filters.Regex("^Add$"),
                                  timer_add),
                   MessageHandler(filters.TEXT & (~ filters.COMMAND) & filters.Regex("^Remove$"),
                                  timer_remove),
                   MessageHandler(filters.TEXT & (~ filters.COMMAND) & filters.Regex("^List$"),
                                  timer_list)],
            NAME: [MessageHandler(filters.TEXT & (~ filters.COMMAND), timer_name)],
            UNIT: [MessageHandler(filters.Regex("^Days$") | filters.Regex("^Hours$") |
                                  filters.Regex("^Minutes$") | filters.Regex("^Seconds$"),
                                  timer_unit)],
            DURATION: [MessageHandler(filters.Regex(INTEGERS_REGEX), timer_duration)],
            REMOVE: [MessageHandler(filters.Regex(INTEGERS_REGEX), timer_remove_core)],
            ConversationHandler.TIMEOUT: [MessageHandler(None, timer_timeout)]
        },
        fallbacks=[CommandHandler("cancel", timer_cancel)],
        conversation_timeout=CHAT_TIMEOUT,
    )
    app.add_handler(timer_handler)

    rng_handler = ConversationHandler(
        entry_points=[CommandHandler("random", rng_start)],
        states={
            LOWER: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_lower)],
            UPPER: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_upper)],
            NUMS: [MessageHandler(filters.Regex(INTEGERS_REGEX), rng_nums)],
            ConversationHandler.TIMEOUT: [MessageHandler(None, rng_timeout)]
        },
        fallbacks=[CommandHandler("cancel", rng_cancel)],
        conversation_timeout=CHAT_TIMEOUT
    )
    app.add_handler(rng_handler)

    weather_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_start)],
        states={
            LOCATION: [MessageHandler(filters.LOCATION, weather_main)],
            ConversationHandler.TIMEOUT: [MessageHandler(None, weather_timeout)]
        },
        fallbacks=[CommandHandler("cancel", weather_cancel)],
        conversation_timeout=CHAT_TIMEOUT
    )
    app.add_handler(weather_handler)

    app.add_handler(CommandHandler("start", received_command))
    app.add_handler(CommandHandler("help", received_command))
    app.add_handler(CommandHandler("status", received_command))
    app.add_handler(CommandHandler("todo", received_command))
    app.add_handler(CommandHandler("news", received_command))
    app.add_handler(CommandHandler("nasa", received_command))
    app.add_handler(CommandHandler("joke", received_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))

    try:
        app.run_polling()
    except NetworkError:
        print('network error - exiting')
        sys.exit()
