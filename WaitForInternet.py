import urllib3
import time

def main():
    while True:
        print('\nattempting internet connection')
        if test_connection() == True:
            print('internet connected')
            break
        else:
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
        else:
            print('error code returned')
            return False
    except Exception as e:
        print('exception occurred')
        return False



# old implementation
def main_old():
    import requests
    import time

    url = 'https://www.google.com'
    timeout = 5
    
    while True:
        print('attempting internet connection')
        try:
            request = requests.get(url, timeout=timeout)
            break
        except (requests.ConnectionError, requests.Timeout) as exception:
            print('internet connection failed')
            print('sleeping for 5s\n')
            time.sleep(5)
            continue

    print('internet connected')
    print()