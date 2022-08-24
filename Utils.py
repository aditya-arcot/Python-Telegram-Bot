import time

def total_time(start):
    return 'total time - {} s'.format(str(round(time.time() - start, 2)))