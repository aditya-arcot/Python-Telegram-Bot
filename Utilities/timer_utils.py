'''contains Timer class'''

import time

class Timer:
    '''maintains custom timer data'''

    def __init__(self, name, chat_id, start, duration):
        self.name = name
        self.chat_id = chat_id
        self.start = start
        self.duration = duration # seconds

    def __str__(self):
        return f'{self.name} - {self.remaining_formatted()}'

    def remaining_seconds(self):
        '''returns number of seconds till timer expiration'''
        return (self.start + self.duration) - int(time.time())

    def remaining_formatted(self):
        '''returns formatted amount of time remaining'''
        seconds = self.remaining_seconds()
        if seconds >= 86400:
            return f'{seconds / 86400:.1f} days remaining'
        if seconds >= 3600:
            return f'{seconds / 3600:.1f} hours remaining'
        if seconds >= 60:
            return f'{seconds / 60:.1f} minutes remaining'
        return f'{seconds:.1f} seconds remaining'
