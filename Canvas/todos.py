'''Core Canvas assignment todo code'''

from datetime import timedelta, datetime
from canvasapi import Canvas
import arrow

import canvas_utils

URL = 'https://utexas.instructure.com'
MIN_DIFF = timedelta()
MAX_DIFF = timedelta(hours=12)

def main(mode, key):
    '''Handles initial call based on mode'''

    if mode == 'all': #send all reminders
        return get_todos(key)

    if mode == 'urgent': #send urgent reminders
        return get_reminders(key)

    return 'illegal mode'

def get_all_todo_attributes(key):
    '''Get attributes of assignment todos (name, date, course_code)'''

    canvas = Canvas(URL, key)
    todos = canvas.get_todo_items()

    all_todo_attributes = []
    for todo in todos:
        data = getattr(todo, 'assignment')

        date = data['due_at']
        #parse due date
        #convert UTC to Central
        #tz changes between -5 and -6 depending on DST
        if date is not None:
            date = arrow.get(date, 'YYYY-MM-DDTHH:mm:ssZ').to('US/Central')

        course_id = data['course_id']
        course = canvas.get_course(course_id)
        course_code = course.course_code.split(' ')
        modified_course_code = (''.join(course_code[:-1]) + ' ' + course_code[-1]).upper()

        all_todo_attributes.append([data['name'], date, modified_course_code])

    #test_attributes = ['test', arrow.get('2022-03-30T10:00:00Z').replace(tzinfo='US/Central')]
    #all_todo_attributes.append(test_attributes)

    return all_todo_attributes


def filter_todos(all_todo_attributes):
    '''Return list of [name, due date, course code, time diff]'''

    filtered_todo_attributes = []

    #check time difference
    for i in all_todo_attributes:
        if i[1] is not None:
            diff = i[1] - arrow.now('US/Central')

            if MIN_DIFF < diff <= MAX_DIFF:
                filtered_todo_attributes.append([i[0], i[1], i[2], diff])

    return filtered_todo_attributes

def sort_todo_attributes(attributes):
    '''Sort attributes by due date'''

    return sorted(attributes, key = lambda x: x[1])

def get_todos(key):
    '''Get todos for the next week'''

    all_todo_attributes = get_all_todo_attributes(key)

    curr = datetime.now()
    if len(all_todo_attributes) == 0:
        curr_date = curr.strftime("%m/%d")
        return [f'{curr_date} No Upcoming Assignments!']

    out = []

    for todo in all_todo_attributes:
        name = canvas_utils.get_output_string(todo[0]) #name
        if todo[1] is not None: #date
            date = todo[1].strftime("%m/%d")
            day = todo[1].strftime('%a')
            time = todo[1].strftime("%H:%M")
            course = todo[2] #course

            out.append(f'{date} ({day}) {time} - {course} - {name}')
        else:
            out.append(name)

    out.sort()

    curr_date = curr.strftime("%m/%d")
    num = len(all_todo_attributes)
    out_str = f'<b><u>{curr_date} Upcoming Assignments ({num})</u></b>'
    for i in out:
        out_str += '\n' + i + '\n'

    return [out_str]

def get_reminders(key):
    '''Get reminders for urgent todos'''

    #list of [name, Arrow object, course code]
    all_todo_attributes = get_all_todo_attributes(key)

    #list of [name, Arrow object, course code, time diff]
    filtered_todo_attributes = sort_todo_attributes(filter_todos(all_todo_attributes))

    out = []
    for todo in filtered_todo_attributes:
        name = canvas_utils.get_output_string(todo[0])
        time_diff = canvas_utils.get_rounded_time_remaining(todo[3])

        string = f'Due in {time_diff[1]}'
        if time_diff[0] == 'm':
            string += ' minute'
            if time_diff[1] > 1:
                string += 's'
            string += '!! - '
        else:
            string += ' hour'
            if time_diff[1] > 1:
                string += 's'
            string += '! - '
        course = todo[2]
        string += f'({course}) ' + name

        out.append(string)

    return out
