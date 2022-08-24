from datetime import timedelta, datetime
from canvasapi import Canvas
import arrow

import CanvasUtils

url = 'https://utexas.instructure.com'

def get_all_todo_attributes(key):
    canvas = Canvas(url, key)
    todos = canvas.get_todo_items()

    all_todo_attributes = []
    for todo in todos:
        data = todo.__getattribute__('assignment')

        date = data['due_at']
        #parse due date
        #convert UTC to Central
        #tz changes between -5 and -6 depending on DST
        if date != None:
            date = arrow.get(date, 'YYYY-MM-DDTHH:mm:ssZ').to('US/Central')

        all_todo_attributes.append([data['name'], date])

    #test_attributes = ['test', arrow.get('2022-03-30T10:00:00Z').replace(tzinfo='US/Central')]
    #all_todo_attributes.append(test_attributes)

    return all_todo_attributes


#out - list of [name, due date, time diff]
min_diff = timedelta()
max_diff = timedelta(hours=12)
def filter_todos(all_todo_attributes):
    filtered_todo_attributes = []

    #check time difference
    for i in all_todo_attributes:
        if i[1] != None:
            diff = i[1] - arrow.now('US/Central')

            if diff > min_diff and diff <= max_diff:
                filtered_todo_attributes.append([i[0], i[1], diff])
    
    return filtered_todo_attributes

def sort_todo_attributes(attributes):
    return sorted(attributes, key = lambda x: x[1])


def get_todos(key):
    all_todo_attributes = get_all_todo_attributes(key)

    curr = datetime.now()
    if len(all_todo_attributes) == 0:
        return ['{} No Upcoming Assignments!'.format(curr.strftime("%m/%d"))]
    else:
        out = []

        for i in all_todo_attributes:
            s = CanvasUtils.get_output_string(i[0])
            if i[1] != None:
                out.append(' - {date} ({day}) {time} {name}'.format(date=i[1].strftime("%m/%d"), day = i[1].strftime('%a'),\
                    time = i[1].strftime("%H:%M"), name = s))
            else:
                out.append(' - {}'.format(s))

        out.sort()
        out.insert(0, '{date} Upcoming Assignments ({num})'.format(date = curr.strftime("%m/%d"), num = len(all_todo_attributes)))
        
    return out

def get_reminders(key):
    all_todo_attributes = get_all_todo_attributes(key) #list of [name, Arrow object]
    filtered_todo_attributes = sort_todo_attributes(filter_todos(all_todo_attributes))

    out = []
    for i in filtered_todo_attributes:
        name = CanvasUtils.get_output_string(i[0])
        t = CanvasUtils.get_rounded_time_remaining(i[2])

        st = 'Assignment due in about {}'.format(t[1])
        if t[0] == 'm':
            st += ' minutes!! - '
        else:
            st += ' hours! - '
        st += name

        out.append(st)
    
    return out


def main(mode, key):
    if mode == 'all': #send all reminders
        return get_todos(key)

    elif mode == 'urgent': #send urgent reminders
        return get_reminders(key)