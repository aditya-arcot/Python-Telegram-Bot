import time

class Timer:
    def __init__(self, name, chat_id, start, duration):
        self.name = name
        self.chat_id = chat_id
        self.start = start
        self.duration = duration # seconds

    def __str__(self):
        return f'{self.name} - {self.remaining_formatted()}'

    def remaining_seconds(self):
        return (self.start + self.duration) - int(time.time())
    
    def remaining_formatted(self):
        seconds = self.remaining_seconds()
        if seconds >= 86400:
            return '{:.1f}'.format(seconds / 86400) + ' days remaining'
        if seconds >= 3600:
            return '{:.1f}'.format(seconds / 3600) + ' hours remaining'
        if seconds >= 60:
            return '{:.1f}'.format(seconds / 60) + ' minutes remaining'
        return '{:.1f}'.format(seconds) + ' seconds remaining'
