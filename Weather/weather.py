'''Weather info for inputted lat, long'''

import os
import sys
from datetime import datetime
import requests


def main(lat, lng):
    '''Formats data from request and returns'''

    request = get_request(lat, lng)

    if 'cod' in request: #request failed
        code = request["cod"]
        print(f'Error code {code}')
        print(request["message"])
        return ['Something went wrong. Please try again']

    out = '<b><u>Weather for current location:</u></b>\n'

    curr = request['current']
    day = request['daily'][0]

    sunrise = datetime.fromtimestamp(day['sunrise'])
    sunset = datetime.fromtimestamp(day['sunset'])

    degree_f = '\u00b0F'

    feels_like = curr['feels_like']
    low = day['temp']['min']
    high = day['temp']['max']
    desc = curr['weather'][0]['description'].capitalize()
    sunrise = datetime.strftime(sunrise, '%-I:%M %p')
    sunset = datetime.strftime(sunset, '%-I:%M %p')

    out += f'- Feels like {feels_like} {degree_f}\n'
    out += f'- Low: {low} {degree_f}, High: {high} {degree_f}\n'
    out += f'- Description: {desc}\n'
    out += f'- Sunrise: {sunrise}, Sunset: {sunset}\n'

    return [out]


def get_request(lat, lng):
    '''Requests weather data from OpenWeather API'''

    path = os.path.join(sys.path[0], '..', 'Weather', 'key.txt')
    with open(path, 'r', encoding = 'ascii') as file:
        api_key = file.readlines()[0].strip()

    url = (f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}'
            f'&exclude=minutely,hourly,alerts&appid={api_key}&units=imperial')

    response = requests.get(url, timeout=5)
    return response.json()
