import logging, sys, os, datetime, time
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import WaitForInternet
WaitForInternet.main()

from telegram import Update, Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, ConversationHandler

import Utils
import RNG
import TelegramUtils

sys.path.insert(1, os.path.join(sys.path[0], '..', 'Canvas'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Weather'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'News'))
sys.path.insert(1, os.path.join(sys.path[0], '..', 'NASA'))

import ReceiveTodoMessageController
import Weather
import News
import NASA

ids, names = TelegramUtils.get_users_info()
token = TelegramUtils.get_token(sandbox=True)
bot = Bot(token)

# returns help messages
def help_msg():
    out = '<b><u>Supported commands:</u></b>\n'
    out += ' - /help\n'
    out += ' - /todo\n'
    out += ' - /weather\n'
    out += ' - /news\n'
    out += ' - /rng min max [n]\n'
    out += ' - /nasa\n'
    out += ' - /clear'
    return [out]

# received message info
# returns - username, user id, msg text, approval status
def msg_info(update, text=True):
    id = update.effective_chat.id
    msg = update.message.text.lower() if text else 'non_text_msg'

    print('--------------------------')
    print(datetime.datetime.now())
    print()

    print('Message received')
    print('Chat id: {}'.format(id))
    print('Message: {}'.format(msg))
    print()

    if id not in ids:
        print('Unapproved sender')
        print()
        return id, msg, False

    print('Approved sender: {}'.format(names[ids.index(id)]))
    print()
    return id, msg, True


LOCATION = 0

async def weather_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id, msg, approved = msg_info(update)
    reply_markup=ReplyKeyboardMarkup(
        [[KeyboardButton(
            text="Send Location",
            request_location=True,
            one_time_keyboard=True)
        ]]
    )
    await TelegramUtils.send_message(bot, id, ['Send location below or press /cancel'], reply_markup=reply_markup)

    return LOCATION

async def weather_main(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id, msg, approved = msg_info(update, text=False)
    loc = update.message.location
    lat, lng = loc['latitude'], loc['longitude']
    out = Weather.main(lat, lng)
    reply_markup=ReplyKeyboardRemove()
    await TelegramUtils.send_message(bot, id, out, reply_markup=reply_markup)

    return ConversationHandler.END

async def weather_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id, msg, approved = msg_info(update)
    await TelegramUtils.send_message(bot, id, ["Weather command canceled"], reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def weather_timeout(update, context):
    id = update.effective_chat.id
    await TelegramUtils.send_message(bot, id, ["Weather command timeout"], reply_markup=ReplyKeyboardRemove())


async def received_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    start = time.time()
    id, msg, approved = msg_info(update)

    msg_lst = msg.split()
    cmd = msg_lst[0][1:]
    args = msg_lst[1:]

    out = []
    if cmd == 'start':
        out = ['<b>Welcome!</b>']
        if not approved:
            out.append('Contact admin for approval!\nProvide id # {}'.format(id))
        else:
            out += help_msg()
    else:
        if approved:
            if cmd == 'help':
                out = help_msg()
            elif cmd == 'ping':
                out = ['pong']
            elif cmd == 'todo':
                out = ReceiveTodoMessageController.main(names[ids.index(id)])
                if out == None:
                    out = ['You are not registered for Canvas todos. Contact admin!']
            elif cmd == 'rng':
                out = RNG.main(args)
            elif cmd == 'clear':
                out = ''
                for i in range(50):
                    out += '﹒\n'
                out = [out]
            elif cmd == 'news':
                out = News.main()
            elif cmd == 'nasa':
                filename, title = NASA.main()
                with open(filename, 'rb') as image:
                    await TelegramUtils.send_photo(bot, id, title, image)
            else:
                print('unknown cmd provided - {} - check code'.format(cmd))
        else:
            out = ['Unauthorized']

    if cmd != 'nasa':
        await TelegramUtils.send_message(bot, id, out, disable_web_page_preview=True if cmd=='news' else None)
    print(Utils.total_time(start))

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    id, msg, approved = msg_info(update)
    if approved:
        await TelegramUtils.send_message(bot, id, ['Command not recognized'] + help_msg())
    else:
        await TelegramUtils.send_message(bot, id ['Unauthorized'])
    print(Utils.total_time(start))

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    id, msg, approved = msg_info(update)
    if approved:
        await TelegramUtils.send_message(bot, id, ['Please use commands, not messages'] + help_msg())
    else:
        await TelegramUtils.send_message(bot, id, ['Unauthorized'])
    print(Utils.total_time(start))

CHAT_TIMEOUT = 30

if __name__ == '__main__':
    app = ApplicationBuilder().token(token).build()

    weather_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_start)],
            states={
                LOCATION: [
                    MessageHandler(filters.LOCATION, weather_main),
                ],
                ConversationHandler.TIMEOUT: [MessageHandler(filters.TEXT | filters.COMMAND, weather_timeout)],
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
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), msg)) #any message

    app.run_polling()
