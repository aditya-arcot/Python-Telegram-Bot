'''Canvas utility functions'''

def get_output_string(string):
    '''Apply other functions and return output string'''

    return shorten_str(remove_dbl_quotes(string), 50)

def remove_dbl_quotes(string):
    '''Remove double quotes in string'''

    return string.replace("\"", "")

def shorten_str(string, trunc):
    '''Truncate string if longer than value specified'''

    return string if len(string) <= trunc else string[0:trunc] + '...'

def get_rounded_time_remaining(timedelta):
    '''Return readable version of timedelta'''

    seconds = timedelta.total_seconds()
    if seconds < 3300: #55 mins
        return ('m', int(seconds/60))
    hours = seconds / 3600
    return ('h', round_to_nearest_tenth(hours))

def round_to_nearest_tenth(num):
    '''Return rounded number without unnecessary 0s'''

    out = round(num * 10) / 10
    split = str(out).split('.')
    if split[1] == '0':
        return int(out)
    return round(out, 2)
