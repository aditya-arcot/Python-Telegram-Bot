'''Weather info for inputted lat, long'''

from datetime import datetime
import requests


def main(lat, lng, api_key):
    '''Formats data from request and returns'''

    url = (f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}'
            f'&exclude=minutely,hourly,alerts&appid={api_key}&units=imperial')

    request = requests.get(url, timeout=5).json()

    if 'cod' in request: #request failed
        code = request["cod"]
        print(f'Error code {code}')
        print(request["message"])
        return ['Something went wrong. Please try again']

    curr = request['current']
    day = request['daily'][0]

    degree_f = '\u00b0F'

    low = day['temp']['min']
    high = day['temp']['max']
    desc = curr['weather'][0]['description'].capitalize()
    sunrise = datetime.strftime(datetime.fromtimestamp(day['sunrise']), '%-I:%M %p')
    sunset = datetime.strftime(datetime.fromtimestamp(day['sunset']), '%-I:%M %p')

    out = ['<b><u>Weather for current location:</u></b>']
    out.append(f'- Feels like {curr["feels_like"]} {degree_f}')
    out.append(f'- Low: {low} {degree_f}, High: {high} {degree_f}')
    out.append(f'- Description: {desc}')
    out.append(f'- Sunrise: {sunrise}, Sunset: {sunset}')
    return out