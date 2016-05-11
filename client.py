'''
    Application: SendOver
    Type       : client script
    Date       : 10th May '16
    Author     : Sanchit Samuel <sanchit.samuel@live.com>
'''

from socket import *
import threading
import time
import os
import sys

PORT = 8000
SERVER = None
HOST = None

def broadcast ():
    info = 'name=user&host='+gethostname()
    broadc = socket(AF_INET, SOCK_DGRAM)
    broadc.bind(('', 0))
    broadc.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    broadc.settimeout(15)

    server_address = ('', 8001)
    broadc.sendto(info, ('<broadcast>', 8001))
    broadc.close()
    '''
    while 1:
        try:
            sent = broadc.sendto(info, ('<broadcast>', 8001))
        except socket.timeout:
            print "timeout"
            broad.shutdown(SHUT_RDWR)
            broad.close()
            break
    if not SERVER:
        print "Broadcast timed out."
        broad.shutdown(SHUT_RDWR)
        broad.close(
        sys.exit()
    '''

def beacon ():
    global SERVER
    while 1:
        if not SERVER:
            broadcast()
        time.sleep(2)

def get_server ():
    global SERVER
    global HOST
    serv = socket(AF_INET, SOCK_STREAM)
    serv.bind(('', 9001))
    serv.listen(5)
    while True:
        c, addr = serv.accept()
        if addr:
            SERVER = addr[0]
            HOST = c.recv(1024)
            serv.close()
            break

def connect_to_server ():
    global SERVER
    FILES = []
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((SERVER, 4000))
    end = None
    files = conn.recv(1024)                                                             # receive list of files
    if '&' in files:
        FILES = files.split('&')
    else:
        FILES.append(files)
    
    file_size = 0
    
    for i in FILES:
        time.sleep(2)
        conn.send(i)                                                                    # send a file location from list
        data = conn.recv(1024)                                                          # receive file info
        if data[:1] == 'S':
            print "Receiving " + os.path.basename(i) + " of size " + data[2:]
            file_size = long(data[2:])
            conn.send('OK')                                                             # send acknolegement to start receive
            f = open('new_'+os.path.basename(i), 'wb')
            data = conn.recv(1024)
            total_reveived = len(data)
            f.write(data)
            check = 0
            while total_reveived < file_size:
                data = conn.recv(1024)
                total_reveived += len(data)
                if len(data) == 0:
                    check = check + 1
                    if check == 1000:
                        break
                percent = "{0:.2f}".format((total_reveived/float(file_size))*100)
                print os.path.basename(i)+'\t\t\t['+str(total_reveived)+': '+(percent)+" %]\r",
                f.write(data)
            print "\n"
            if check == 1000:
                print "Error while transfering data"
    
    conn.close()

def main ():
    global SERVER
    global HOST
    
    broad = threading.Thread(target=beacon)
    broad.setDaemon(True)
    broad.start()
    
    print "Waiting for connection"
    # serv = threading.Thread(target=get_server)
    # serv.setDaemon(True)
    # serv.start()
    get_server()
    print "Starting to receive files from " + str(HOST)
    connect_to_server()
    
    
if __name__ == '__main__':
    main()
