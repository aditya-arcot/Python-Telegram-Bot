'''archives, deletes log files'''

import datetime
import os
import time
import sys

'''
Archive yesterday's logs
Delete logs older than a week
'''

'''
Each program run through cron appends output to a uniquely named log
This program runs at 12:00 AM daily
System restarts at 12:05 AM daily, which restarts logging into new files
'''

'''
Process
    Archive
        Yesterday's date is appended to each log file
            Ex: udp_listener.txt -> udp_listener_log_01-01-23.txt
        Log files are moved to archived folder
    Delete
        Log files in archived folder with a date older than 1 week are deleted
'''

start = time.time()

curr_date = datetime.datetime.now()
print(curr_date)

yesterday = curr_date - datetime.timedelta(days=1)
yesterday_str = yesterday.strftime("%m-%d-%y")

log_path = os.path.join(sys.path[0], '..', 'Logs')
archived_log_path = os.path.join(log_path, 'archived')

if not os.path.exists(log_path):
    os.makedirs(log_path)
if not os.path.exists(archived_log_path):
    os.makedirs(archived_log_path)


#archive logs
archived = []
logfiles = [f for f in os.listdir(log_path) if os.path.isfile(os.path.join(log_path, f))]
for f in logfiles:
    split = os.path.splitext(f)
    if split[1] == ".txt":
        os.rename(os.path.join(log_path, f), os.path.join(
            archived_log_path, split[0] + "_" + yesterday_str + ".txt")
        )
        archived.append(f)

print(f'archived {len(archived)} logs')
for i in archived:
    print(' - ' + i)
print()


#delete logs more than 1 week old
deleted = []
archived_logfiles = [f for f in os.listdir(archived_log_path)
    if os.path.isfile(os.path.join(archived_log_path, f))]
for f in archived_logfiles:
    split = os.path.splitext(f)
    if split[1] == ".txt":
        split = split[0].split('_')
        date = datetime.datetime.strptime(split[-1], "%m-%d-%y")
        days = (curr_date - date).days
        if days > 7: #delete log
            os.remove(os.path.join(archived_log_path, f))
            deleted.append(f)

print(f'deleted {len(deleted)} logs')
for i in deleted:
    print(' - ' + i)

print('\nruntime -', str(round(time.time() - start, 2)) + ' s\n')
