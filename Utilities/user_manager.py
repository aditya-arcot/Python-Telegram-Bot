'''module contining User, UserManager classes'''

import json
from typing import List

class User:
    '''allows access to user properties'''

    def __init__(self, info: dict):
        self.name = info.get('name')
        self.telegram_status = info.get('telegram_status')
        if self.telegram_status == 'active': # don't read if inactive
            self.telegram_id = info.get('telegram_id')
        else:
            self.telegram_id = None
        self.canvas_status = info.get('canvas_status')
        if self.canvas_status == 'active': # don't read if inactive
            self.canvas_key = info.get('canvas_key')
            self.canvas_url = info.get('canvas_url')
        else:
            self.canvas_key = None
            self.canvas_url = None

    def __repr__(self) -> str:
        out = []
        out.append(f'user:\t\t{self.name}')
        if self.telegram_status == 'active':
            out.append(f'telegram:\t{self.telegram_id[0:5]}***')
        else:
            out.append('telegram:\tinactive')
        if self.canvas_status == 'active':
            out.append(f'canvas:\t\t{self.canvas_key[0:5]}*** ' + \
                       ('(default url)' if self.canvas_url is None else f'({self.canvas_url})'))
        else:
            out.append('canvas:\t\tinactive')
        return '\n' + '\n'.join(out) + '\n'''


class UserManager:
    '''reads in users, creates objects, allows access'''

    def __init__(self, users_json):
        with open(users_json, 'r') as json_file:
            contents = json.loads(json_file.read())

        self.all_users = [User(info) for info in contents]

    def get_user_from_telegram_id(self, telegram_id) -> User:
        '''returns User object for given Telegram id'''
        telegram_id = str(telegram_id)
        for user in self.all_users:
            if user.telegram_id == telegram_id:
                return user
        return None

    def get_all_active_telegram_users(self) -> List[User]:
        '''returns list of active Telegram users'''
        telegram_users = []
        for user in self.all_users:
            if user.telegram_status == 'active':
                telegram_users.append(user)
        return telegram_users

    def get_all_active_canvas_telegram_users(self) -> List[User]:
        '''returns list of users active for both Canvas and Telegram'''
        canvas_telegram_users = []
        for user in self.get_all_active_telegram_users():
            if user.canvas_status == 'active':
                canvas_telegram_users.append(user)
        return canvas_telegram_users
