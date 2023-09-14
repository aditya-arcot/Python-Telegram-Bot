''' Joke from icanhazdadjoke.com '''

import requests

def main():
    ''' Makes request, returns joke '''

    url = 'https://icanhazdadjoke.com'
    request = requests.get(url, headers={'Accept':'application/json'}, timeout=5).json()
    if 'joke' in request:
        return [request['joke']]
    return ['Something went wrong. Please try again']
