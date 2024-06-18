'''Pauses main program until Internet connection is established'''

import time
import urllib3

def main():
    '''Loop for checking for Internet connection'''

    curr_time = 0
    max_time = 60

    while curr_time < max_time:
        print('\nattempting internet connection')
        if test_connection():
            print('internet connected\n')
            return
        print('sleeping for 5s')
        time.sleep(5)
        curr_time += 5

    print('\nmax time (60s) exceeded')
    print('rerun calling program when internet connection is restored')

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
