'''NASA picture of the day'''

import os
from datetime import date
import urllib.request
import nasapy

def main(api_key):
    '''
    Gets picture of the day info
    Checks if local file is updated & downloads if not
    Returns file and title
    '''

    image_path = os.path.join('resources', 'nasa-pod')
    last_update_path = os.path.join('resources', 'nasa-last-update')

    url, title = get_pic_info(api_key)

    if url is None:
        print('skipping')
        return None, title

    today_str = str(date.today())

    updated = ''
    try:
        with open(last_update_path, 'r', encoding='ascii') as file:
            updated = file.readlines()[0].strip('\n')
    except FileNotFoundError:
        print('last-updated file not present')

    if updated != today_str:
        print('pic not updated - downloading pic, updating last-updated')
        if os.path.exists(image_path):
            os.remove(image_path)
        urllib.request.urlretrieve(url, image_path)
        with open(last_update_path, 'w', encoding='ascii') as file:
            file.write(today_str)

    return os.path.abspath(image_path), title


def get_pic_info(api_key):
    '''Requests NASA API for picture of the day url and title'''

    nasa = nasapy.Nasa(key = api_key)

    pic = nasa.picture_of_the_day()
    title = pic['title']

    if not 'hdurl' in pic.keys():
        print('no picture for today, only video')
        return None, title

    url = pic['hdurl']

    return url, title
