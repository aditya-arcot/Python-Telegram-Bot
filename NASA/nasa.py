'''NASA picture of the day'''

import os
import sys
from datetime import date
import urllib.request
import nasapy

FILENAME = 'nasa-pod'
NASA_DIR = os.path.join(sys.path[0], '..', 'NASA')


def main():
    '''
    Gets picture of the day info
    Checks if local file is updated & downloads if not
    Returns file and title
    '''

    url, title = get_pic_info()
    today_str = str(date.today())

    updated = ''
    try:
        with open(os.path.join(NASA_DIR, 'last-updated'), 'r', encoding='ascii') as file:
            updated = file.readlines()[0].strip('\n')
    except FileNotFoundError:
        print('last-updated file not present')

    if updated != today_str:
        print('pic not updated - downloading pic, updating last-updated')
        urllib.request.urlretrieve(url, os.path.join(NASA_DIR, FILENAME))
        with open(os.path.join(NASA_DIR, 'last-updated'), 'w', encoding='ascii') as file:
            file.write(today_str)

    return os.path.abspath(os.path.join(NASA_DIR, FILENAME)), title


def get_pic_info():
    '''Requests NASA API for picture of the day url and title'''

    path = os.path.join(NASA_DIR, 'key.txt')
    with open(path, 'r', encoding='ascii') as file:
        api_key = file.readlines()[0].strip()

    nasa = nasapy.Nasa(key = api_key)

    pic = nasa.picture_of_the_day()
    title = pic['title']
    url = pic['hdurl']

    return url, title
