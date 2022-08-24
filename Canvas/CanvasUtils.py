import os, sys

get_output_string = lambda s: shorten_str(remove_dbl_quotes(s), 50)

remove_dbl_quotes = lambda s: s.replace("\"", "")

shorten_str = lambda s, n: s if len(s) <= n else s[0:n] + '...'

def get_rounded_time_remaining(td):
    s = td.total_seconds()
    if s < 3300: #55 mins
        return ('m', int(s/60))
    h = s / 3600
    return ('h', round_to_nearest_tenth(h))

def round_to_nearest_tenth(n):
    out = round(n * 10) / 10
    split = str(out).split('.')
    if split[1] == '0':
        return int(out)
    return round(out, 2)

def get_canvas_users_info():
    path = os.path.join(sys.path[0], '..', 'Canvas', 'users.txt')
    f = open(path, "r")

    names, keys = [], []
    for line in f:
        lst = line.strip().split('\t')

        names.append(lst[0])
        keys.append(lst[1])

    f.close()

    return names, keys
