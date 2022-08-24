import Todos
import CanvasUtils

names, keys = CanvasUtils.get_canvas_users_info()

def main(name):
    if name in names:
        key = keys[names.index(name)]
        return Todos.main('all', key)
    else:
        return
