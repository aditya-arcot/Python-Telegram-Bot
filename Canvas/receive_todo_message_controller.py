'''Connects telegram_listener and todos'''

import todos
import canvas_utils

names, keys = canvas_utils.get_canvas_users_info()

def main(name):
    '''Check if name is connected to Canvas and return todos'''

    if name in names:
        key = keys[names.index(name)]
        return todos.main('all', key)
    return []
