import time
import urllib3

def main():
    while True:
        print('\nattempting internet connection')
        if test_connection():
            print('internet connected\n')
            break
        print('sleeping for 5s')
        time.sleep(5)

def test_connection():
    http = urllib3.PoolManager(timeout=3)

    try :
        r = http.request('GET', 'google.com', preload_content=False)
        code = r.status
        r.release_conn()
        if code == 200:
            print('success')
            return True
        print(f'error code returned: {code}')
        return False
    except Exception as e:
        print(f'exception occurred: {e}')
        return False
