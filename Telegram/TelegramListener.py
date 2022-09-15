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

# NASA dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'NASA'))

import RNG
import Weather
import ReceiveTodoMessageController
import TelegramUtils
import Utils
import News
import NASA

# read Telegram user info
ids, names = TelegramUtils.get_users_info()

token = TelegramUtils.get_token()

# returns help messages
def help_msg():
    out = '<b><u>Supported commands:</u></b>\n'
    out += ' - /help\n'
    out += ' - /todo\n'
    out += ' - /weather\n'
    out += ' - /news\n'
    out += ' - /rng min max [n]\n'
    out += ' - /ping\n'
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

async def received_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    start = time.time()
    user, id, msg, approved = msg_info(update)

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
            elif cmd == 'weather':
                out = Weather.main()
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
                url, title = NASA.main()
                asyncio.get_event_loop().run_until_complete(
                    bot.send_photo(photo=url, chat_id=id, caption=title)
                )
            else:
                print('unknown cmd provided - {} - check code'.format(cmd))
        else:
            out = ['Unauthorized']

    if cmd != 'nasa':
        await TelegramUtils.reply(update, out, disable_web_page_preview=True if cmd=='news' else None)
    print(Utils.total_time(start))

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
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", received_command))
    app.add_handler(CommandHandler("help", received_command))
    app.add_handler(CommandHandler("ping", received_command))
    app.add_handler(CommandHandler("weather", received_command))
    app.add_handler(CommandHandler("todo", received_command))
    app.add_handler(CommandHandler("rng", received_command))
    app.add_handler(CommandHandler("clear", received_command))
    app.add_handler(CommandHandler("news", received_command))
    app.add_handler(CommandHandler("nasa", received_command))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command)) #unknown command
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), msg)) #any message

    app.run_polling()
