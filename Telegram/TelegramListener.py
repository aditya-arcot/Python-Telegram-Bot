import logging, sys, os, datetime, time
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s',
    level=logging.INFO
)

# parent dir
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import WaitForInternet
WaitForInternet.main()

from telegram import Update
from telegram.ext import filters, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes

# Canvas dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Canvas'))

# Weather dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Weather'))

# News dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'News'))

import RNG
import Weather
import ReceiveTodoMessageController
import TelegramUtils
import Utils
import News

# read Telegram user info
ids, names = TelegramUtils.get_users_info()

token = TelegramUtils.get_token()

# returns help messages
def help_msg():
    out = '<b><u>Supported commands:</u></b>\n'
    out += ' - /help\n'
    out += ' - /ping\n'
    out += ' - /weather\n'
    out += ' - /todo\n'
    out += ' - /rng min max [n]\n'
    out += ' - /clear'
    return [out]

# received message info
# returns - username, user id, msg text, approval status
def msg_info(update):
    user = update.effective_chat.username
    id = update.effective_chat.id
    msg = update.message.text.lower()

    print('--------------------------')
    print(datetime.datetime.now())
    print()

    print('Message received')
    print('Username: {}'.format(user))
    print('Chat id: {}'.format(id))
    print('Message: {}'.format(msg))
    print()

    if id not in ids:
        print('Unapproved sender')
        print()
        return user, id, msg, False

    print('Approved sender: {}'.format(names[ids.index(id)]))
    print()
    return user, id, msg, True

async def received_command(update:Update, context:ContextTypes.DEFAULT_TYPE, cmd):
    start = time.time()
    user, id, msg, approved = msg_info(update)

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
            elif cmd == 'weather':
                out = Weather.main()
            elif cmd == 'todo':
                out = ReceiveTodoMessageController.main(names[ids.index(id)])
                if out == None:
                    out = ['You are not registered for Canvas todos. Contact admin!']
            elif cmd == 'rng':
                out = RNG.main(context.args)
            elif cmd == 'clear':
                out = ''
                for i in range(50):
                    out += '﹒\n'
                out = [out]
            elif cmd == 'news':
                out = News.main()
            else:
                print('unknown cmd provided - {} - check code'.format(cmd))
        else:
            out = ['Unauthorized']

    await TelegramUtils.reply(update, out, disable_web_page_preview=True if cmd=='news' else None)
    print(Utils.total_time(start))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'start')

# help command received
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'help')

# ping command received
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'ping')

# weather command received
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'weather')

# todo command received
async def todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'todo')

# rng command received
async def rng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'rng')

# clear command received
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'clear')

# news command received
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await received_command(update, context, 'news')

# other commands received
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    user, id, msg, approved = msg_info(update)
    if approved:
        await TelegramUtils.reply(update, ['Command not recognized'] + help_msg())
    else:
        await TelegramUtils.reply(update, ['Unauthorized'])
    print(Utils.total_time(start))

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    user, id, msg, approved = msg_info(update)
    if approved:
        await TelegramUtils.reply(update, ['Please use commands, not messages'] + help_msg())
    else:
        await TelegramUtils.reply(update, ['Unauthorized'])
    print(Utils.total_time(start))


if __name__ == '__main__':
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    ping_handler = CommandHandler("ping", ping)
    weather_handler = CommandHandler("weather", weather)
    todo_handler = CommandHandler("todo", todo)
    rng_handler = CommandHandler("rng", rng)
    clear_handler = CommandHandler("clear", clear)
    news_handler = CommandHandler("news", news)
    unknown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), msg)

    app = ApplicationBuilder().token(token).build()

    app.add_handler(start_handler)
    app.add_handler(help_handler)
    app.add_handler(ping_handler)
    app.add_handler(weather_handler)
    app.add_handler(todo_handler)
    app.add_handler(rng_handler)
    app.add_handler(clear_handler)
    app.add_handler(news_handler)
    app.add_handler(unknown_command_handler)
    app.add_handler(message_handler)

    app.run_polling()
