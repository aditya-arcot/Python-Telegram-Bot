# Telegram-Bot


## Description  
Multi-purpose Telegram bot  
Source code written in Python   


## Commands
- /help - available commands
- /todo - Canvas todos
  - works for following districts - UT Austin, UTHealth, HoustonISD
- /weather - local weather info
  - based on user-inputted location
- /news - top 10 US news headlines
- /nasa - NASA astronomy pic of the day
- /rng - random number generator
  - based on user-provided parameters
- /clear - clear screen


## Required files
Omitting a Telegram file will render the bot unable to communicate at all, but omitting a specific feature file will only affect that feature
- Weather/key.txt
  - [OpenWeather API](https://openweathermap.org) key 
- NASA/key.txt
  - [NASA APOD API](https://api.nasa.gov) key 
- News/key.txt
  - [News API](https://newsapi.org) key
- Telegram/token.txt
  - [Telegram bot](https://core.telegram.org/bots/features#botfather) token
- Telegram/users.txt
  - Each line contains a name and the corresponding Telegram user ID, separated by a tab
  - User names are arbitrary, but should match an entry in Canvas users file for users that are registered for Canvas
- Canvas/users.txt
  - Each line contains a name and CanvasAPI key, separated by a tab
  - Keys can be generated under Settings on Canvas opened in a browser
  - Additionally, if the Canvas base URL is not the default (https://utexas.instructure.com), it must be specified after the Canvas API key, separated by a tab
  - Todo functionality is attempted for unsupported versions of Canvas, but it may cause unexpected errors


## Non-standard dependencies
Install using pip
- Python Telegram Bot (python-telegram-bot) 20.0
- Canvas API (canvasapi) 3.0.0
- NasaPy (nasapy) 0.2.7
- Pandas (pandas) 1.5.2


## Usage
- telegram_listener.py
  - listen for commands given to Telegram bot
  - runs continuously after being called
- reminders_controller.py urgent
  - send urgent reminders to users
  - runs once
- reminders_controller.py all
  - send all reminders to users
  - runs once
- news_controller.py
  - send headlines to users
  - runs once
  
