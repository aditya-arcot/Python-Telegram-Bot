'''module containing KeyManager class'''

import configparser
import sys

class KeyManager:
    '''reads in config, keys and allows access'''

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.mode = 'prod'
        if 'options' in config.sections() and 'mode' in config.options('options'):
            self.mode = config.get('options', 'mode')
        if self.mode not in ('prod', 'dev'):
            print('unknown mode - check file')
            sys.exit()

        self.api_keys = {}
        if 'APIs' in config.sections():
            for key in config.options('APIs'):
                self.api_keys[key] = config.get('APIs', key)

        if self.mode == 'prod':
            assert 'telegram_key' in self.api_keys
        else:
            assert 'telegram_sandbox_key' in self.api_keys

        assert 'weather_key' in self.api_keys
        assert 'news_key' in self.api_keys
        assert 'nasa_key' in self.api_keys

    def get_weather_key(self):
        '''returns weather API key'''
        return self.api_keys['weather_key']

    def get_news_key(self):
        '''returns news API key'''
        return self.api_keys['news_key']

    def get_nasa_key(self):
        '''returns NASA API key'''
        return self.api_keys['nasa_key']

    def get_telegram_key(self):
        '''returns Telegram bot key based on current environment'''
        if self.mode == 'prod':
            return self.api_keys['telegram_key']
        return self.api_keys['telegram_sandbox_key']
