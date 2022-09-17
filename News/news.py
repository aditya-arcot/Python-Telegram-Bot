'''News headlines'''

import os
import sys
import requests

def main():
    '''
    Request headlines from News API
    Format and return
    '''

    path = os.path.join(sys.path[0], '..', 'News', 'key.txt')
    with open(path, 'r', encoding = 'ascii') as file:
        api_key = file.readlines()[0].strip()

    api = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}&pageSize=10"
    req = requests.get(api, timeout=5)
    req_json = req.json()

    out = '<b><u>Top US headlines:</u></b>\n'
    for i in req_json['articles']:
        source = i['source']['name']
        title = ' '.join(i['title'].split('-')[:-1])
        url = i['url']

        if source is not None and title is not None and url is not None:
            out += title + f" - <a href='{url}'>{source}</a>\n\n"

    return [out]
