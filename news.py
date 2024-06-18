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

    out = ['<b><u>Top US headlines:</u></b>']
    for i in req_json['articles']:
        title = i['title']
        if (not title) or (title == "[Removed]"):
            continue
        title = ' '.join(title.split('-')[:-1])

        source = i['source']['name']
        if not source:
            continue

        url = i['url']
        if not url:
            continue

        out.append(f"{title.strip()} - <a href='{url}'>{source}</a>")

    return out
