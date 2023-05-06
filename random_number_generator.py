'''Generates specified number of random numbers between lower and upper bounds'''

import random
import time

def main(args):
    '''Checks arguments and calls rand_generator'''

    lower = int(args[0])
    upper = int(args[1])
    nums = int(args[2])

    if upper < lower:
        return ['Upper bound less than lower bound']

    return rand_generator(lower, upper, nums)

def rand_generator(lower, upper, nums = 1):
    '''Core code for generating random numbers'''
    random.seed(int(time.time()))
    return ['<b><u>Random numbers:</u></b>'] + \
        [str(random.randint(lower, upper)) for _ in range(nums)]
