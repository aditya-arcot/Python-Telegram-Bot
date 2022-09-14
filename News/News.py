import requests
import os
import sys


def main():
    path = os.path.join(sys.path[0], '..', 'News', 'key.txt')
    with open(path, 'r') as f:
        api_key = f.readlines()[0].strip()

    api = "https://newsapi.org/v2/top-headlines?country=us&apiKey={}&pageSize=10".format(api_key)
    req = requests.get(api)
    d = req.json()

    out = '<b><u>Top US headlines:</u></b>\n'
    for n, i in enumerate(d['articles']):

        source = i['source']['name']
        title = ' '.join(i['title'].split('-')[:-1])
        url = i['url']

        if source != None and title != None and url != None:
            out += title + " - <a href='{}'>{}</a>\n\n".format(url, source)

    #TelegramUtils.new_message(bot, id, [out], disable_web_page_preview=True)
    return [out]
