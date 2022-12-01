import socket
import datetime
import subprocess

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 50200))

while True:
    data = sock.recv(256)
    print(datetime.datetime.now()) 
    print('-> data received')

    try:
        data = data.decode().strip()
    except:
        print('-> exception')
        print(data)
        continue
        
    print(data)

    if data == 'wake desktop':
        process = subprocess.Popen(['wakeonlan', '-p', '50200', 'A4:BB:6D:54:ED:8C'], 
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        print('-> ran command')
        print('-> stdout:')
        print(stdout.decode().strip())
        print()
        print('-> stderr:')
        print(stderr.decode().strip())
        print()
            


    print()

