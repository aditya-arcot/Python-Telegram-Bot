'''Generates specified number of random numbers between lower and upper bounds'''

import random
import time

def main(args):
    '''Checks & formats arguments and calls rand_generator'''

    if len(args) < 2:
        return ['Too few arguments']
    if len(args) > 3:
        return ['Too many arguments']

    args_int = []
    for i in args:
        try:
            args_int.append(int(i))
        except ValueError:
            return ['Please input integers']

    lower = args_int[0]
    upper = args_int[1]
    if upper < lower:
        return ['Upper bound less than lower bound']

    if len(args_int) == 2:
        return rand_generator(lower, upper)
    nums = args_int[2]
    return rand_generator(lower, upper, nums)

def rand_generator(lower, upper, nums = 1):
    '''Core code for generating random numbers'''

    seed = int(time.time())
    random.seed(seed)

    out = f'<b><u>{nums} random number(s) between {lower} and {upper}</u></b>'
    out += f'\nseed: {seed}'
    for _ in range(nums):
        out += '\n' + str(random.randint(lower, upper))
    return [out]
