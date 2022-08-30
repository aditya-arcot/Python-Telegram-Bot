import datetime, time, sys, os

# add parent dir
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import WaitForInternet
WaitForInternet.main()

from telegram import Update
from telegram.ext import Updater, CallbackContext, MessageHandler, CommandHandler, Filters

# add Canvas dir
sys.path.insert(1, os.path.join(sys.path[0], '..', 'Canvas'))

import Weather
import ReceiveTodoMessageController
import TelegramUtils
import Utils

ids, names = TelegramUtils.get_users_info()
token = TelegramUtils.get_token()

# output - username, id, message, approval status
def intro(update):
    user = update.message.from_user.username
    id = update.message.from_user.id
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

# output - 
def start(update: Update, context: CallbackContext):
    start = time.time()
    _, id, _, approved = intro(update)

    out = []
    out.append('Welcome!')
    if not approved:
        out.append('Contact admin for approval!')
        out.append('Provide id # {}'.format(id))
    else:
        out += help_msg()
    TelegramUtils.send_reply_messages(update, out)
    
    print(Utils.total_time(start))

def help_msg():
    out = []
    out.append('Supported commands:')
    out.append(' - help')
    out.append(' - ping (system test)')
    out.append(' - weather')
    out.append(' - todo')
    return out

todo_variations = ['todo', 'todos', 'to do', 'to dos', 'to-do', 'to-dos']

def handle_message(update: Update, context: CallbackContext):
    start = time.time()
    _, id, msg, approved = intro(update)
    
    messages = []

    if approved:
        if msg == 'help':
            print('Command - help')
            messages = help_msg()

        #test
        elif msg == 'ping':
            print('Command - test message')
            messages = ['pong']

        #current weather
        elif msg == 'weather':
            print('Command - weather')
            messages = Weather.main()
        
        #Canvas todos
        elif msg in todo_variations:
            print('Command - todos')
            out = ReceiveTodoMessageController.main(names[ids.index(id)])
            if out == None:
                messages = ['You are not registered for Canvas todos. Contact admin!']
            else:
                messages = out

        else:
            messages = ['Command not recognized']

    else:
        messages = ['Unauthorized']

    TelegramUtils.send_reply_messages(update, messages)

    print(Utils.total_time(start))
    #sys.stdout.flush() #use -u flag when running instead

updater = Updater(token)
dispatcher = updater.dispatcher
dispatcher.add_handler(MessageHandler(Filters.text & ~ Filters.command, handle_message))
dispatcher.add_handler(CommandHandler('start', start))
updater.start_polling()
updater.idle()
