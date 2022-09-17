'''General use utility functions'''

import time

def total_time(start):
    '''Returns formatted total time given start time'''

    return f'total time - {str(round(time.time() - start, 2))} s'
