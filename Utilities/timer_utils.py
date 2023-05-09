import time

class Timer:
    def __init__(self, name, chat_id, start, duration):
        self.name = name
        self.chat_id = chat_id
        self.start = start
        self.duration = duration # seconds

    def __str__(self):
        return f'{self.name} - {self.remaining()}s left'

    def remaining(self):
        return (self.start + self.duration) - int(time.time())
    