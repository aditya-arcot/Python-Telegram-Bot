'''Connects telegram_listener and todos'''

import todos
import canvas_utils

names, keys, URLs = canvas_utils.get_canvas_users_info()

def main(name):
    '''Check if name is connected to Canvas and return todos'''

    if name in names:
        ind = names.index(name)
        key = keys[ind]
        URL = URLs[ind]
        return todos.main('all', key, URL)
    return []
