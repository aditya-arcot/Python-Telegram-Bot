'''News headlines'''

import requests

def main(api_key):
    '''
    Request headlines from News API
    Format and return
    '''

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
