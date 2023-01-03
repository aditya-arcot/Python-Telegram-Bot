'''Pauses main program until Internet connection is established'''

import time
import urllib3

def main():
    '''Loop for checking for Internet connection'''

    while True:
        print('\nattempting internet connection')
        if test_connection():
            print('internet connected\n')
            break
        print('sleeping for 5s')
        time.sleep(5)

def test_connection():
    '''Core code for checking internet connection'''

    http = urllib3.PoolManager(timeout=3)

    try :
        request = http.request('GET', 'google.com', preload_content=False)
        code = request.status
        request.release_conn()
        if code == 200:
            print('success')
            return True
        print(f'error code returned: {code}')
        return False
    except urllib3.exceptions.MaxRetryError:
        print('exception occurred: MaxRetryError')
        return False
