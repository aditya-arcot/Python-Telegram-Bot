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

    seed = int(time.time())
    random.seed(seed)

    out = []
    for _ in range(nums):
        out.append(str(random.randint(lower, upper)))
    out.append(f'seed: {seed}')
    return ['\n'.join(out)]
