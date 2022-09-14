import requests
import geocoder
from datetime import datetime
import os
import sys

def main():
    try:
        g = geocoder.ip('me')
        latlng = g.latlng
        lat = latlng[0]
        lng = latlng[1]

        path = os.path.join(sys.path[0], '..', 'Weather', 'key.txt')
        with open(path, 'r') as f:
            api_key = f.readlines()[0].strip()

        url = ('https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lng}'
                '&exclude=minutely,hourly,alerts&appid={api}&units=imperial')\
                .format(lat = lat, lng = lng, api = api_key)

        response = requests.get(url)
        x = response.json()

        if 'cod' in x: #only when request fails
            print('Error code {}'.format(x["cod"]))
            print(x["message"])
        else:
            out = '<b><u>Weather for {}, {}:</u></b>\n'.format(g.city, g.state)

            curr = x['current']
            day = x['daily'][0]

            sunrise = datetime.fromtimestamp(day['sunrise'])
            sunset = datetime.fromtimestamp(day['sunset'])

            F = '\u00b0F'
            out += '- Feels like {} {}\n'.format(curr['feels_like'], F)
            out += '- Low: {} {}, High: {} {}\n'.format(day['temp']['min'], F, day['temp']['max'], F)
            out += '- Description: {}\n'.format(curr['weather'][0]['description'].capitalize())
            out += '- Sunrise: {}, Sunset: {}\n'\
                .format(datetime.strftime(sunrise, '%-I:%M %p'),datetime.strftime(sunset, '%-I:%M %p'))

            return [out]

    except Exception as e:
        print(e)
