import os
import sys
import nasapy


def main():
    path = os.path.join(sys.path[0], '..', 'NASA', 'key.txt')
    with open(path, 'r') as f:
        api_key = f.readlines()[0].strip()

    nasa = nasapy.Nasa(key = api_key)

    pic = nasa.picture_of_the_day()
    title = pic['title']
    url = pic['hdurl']

    return url, title
