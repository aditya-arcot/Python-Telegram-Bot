import os
import sys
from datetime import date
import nasapy
import urllib.request

filename = 'nasa-pod'

nasa_dir = os.path.join(sys.path[0], '..', 'NASA')

def get_pic_info():
    path = os.path.join(nasa_dir, 'key.txt')
    with open(path, 'r') as f:
        api_key = f.readlines()[0].strip()

    nasa = nasapy.Nasa(key = api_key)

    pic = nasa.picture_of_the_day()
    title = pic['title']
    url = pic['hdurl']

    return url, title

def main():
    url, title = get_pic_info()

    today_str = str(date.today())

    updated = ''
    try:
        with open(os.path.join(nasa_dir, 'last-updated'), 'r') as f:
            updated = f.readlines()[0].strip('\n')
    except Exception as _:
        print('last-updated file not present')

    if updated != today_str:
        print('pic not updated')
        urllib.request.urlretrieve(url, os.path.join(nasa_dir, filename))
        with open(os.path.join(nasa_dir, 'last-updated'), 'w') as f:
            f.write(today_str)

    return os.path.abspath(os.path.join(nasa_dir, filename)), title
