'''Core Canvas assignment todo code'''

from datetime import timedelta, datetime
from ssl import SSLCertVerificationError
import re

from canvasapi import Canvas
import arrow

from Utilities import canvas_utils

MIN_DIFF = timedelta()
MAX_DIFF = timedelta(hours=12)
DEFAULT_URL = 'https://utexas.instructure.com'

def main(mode, key, url):
    '''Handles initial call based on mode'''

    if url is None:
        url = DEFAULT_URL

    if mode == 'all': #send all reminders
        return get_todos(key, url)

    if mode == 'urgent': #send urgent reminders
        return get_reminders(key, url)

    print('illegal mode')
    return []

def get_all_todo_attributes(key, url):
    '''Get attributes of assignment todos (name, date, course_code)'''

    canvas = Canvas(url, key)
    todos = canvas.get_todo_items()

    all_todo_attributes = []

    try:
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
            modified_course_code = course_code
            if 'houston' in url:
                modified_course_code = ' '.join(course_code[:-5])
            elif 'utexas' in url:
                modified_course_code = (''.join(course_code[:-1]) + ' ' + course_code[-1]).upper()
            elif 'uth' in url:
                course_code = [i for i in re.split(r'(\d+)', ''.join(course_code)) if i != ''][1:-1]
                modified_course_code = course_code[0] + ' ' + ''.join(course_code[1:])

            all_todo_attributes.append([data['name'], date, modified_course_code])
    except SSLCertVerificationError:
        print('SSLCertVerificationError - exiting')
        print()
        print()

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

def get_todos(key, url):
    '''Get todos for the next week'''

    all_todo_attributes = get_all_todo_attributes(key, url)

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
    out.insert(0, f'<b><u>{curr_date} Upcoming Assignments ({num})</u></b>')

    return out

def get_reminders(key, url):
    '''Get reminders for urgent todos'''

    #list of [name, Arrow object, course code]
    all_todo_attributes = get_all_todo_attributes(key, url)

    #list of [name, Arrow object, course code, time diff]
    filtered_todo_attributes = sort_todo_attributes(filter_todos(all_todo_attributes))

    out = []
    for todo in filtered_todo_attributes:
        name = canvas_utils.get_output_string(todo[0])
        time_diff = canvas_utils.get_rounded_time_remaining(todo[3])

        string = f'Due in {time_diff[1]}'
        if time_diff[0] == 'm':
            string += ' minute'
            if time_diff[1] != 1:
                string += 's'
            string += '!! - '
        else:
            string += ' hour'
            if time_diff[1] != 1:
                string += 's'
            string += '! - '
        course = todo[2]
        string += f'({course}) ' + name

        out.append(string)

    return out
