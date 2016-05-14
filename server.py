'''
    Application: SendOver
    Type       : server script
    Date       : 10th May '16
    Author     : Sanchit Samuel <sanchit.samuel@live.com>
'''
from socket import *
import os
import threading
import time
import sys

PORT = 8000
CLIENT = {}
FILES = []
TO_SEND = None

def send_over (filename, sock):
    if os.path.isfile(filename):
        sock.send("S " + str(os.path.getsize(filename)))                    # send file info
        userResponse = sock.recv(1024)                                      # wait for user acknolegement
        if userResponse[:2] == 'OK':
            with open(filename, "rb") as f:
                bytes = f.read(1024)
                sock.send(bytes)
                while bytes != "":
                    bytes = f.read(1024)
                    sock.send(bytes)
                    percentage = sock.recv(1024)
                    print percentage + "% sent \r",
                sock.send('END')
                print "Done"
    else:
        sock.send("ERR")
    
    sock.close()
    
def look_for_clients ():
    tries = 4
    global TO_SEND
    while 1:
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('',8001))
        m = s.recvfrom(4096)
        variables = m[0].split('&')
        tmp, name = variables[0].split('=', 1)
        tmp, host = variables[1].split('=', 1)
        global CLIENT
        CLIENT[host] = m[1][0]
        
def initiate_client (ip):
    print "Connecting to " + ip
    init = socket(AF_INET, SOCK_STREAM)
    init.connect((ip, 9001))
    init.send(gethostname())
    init.close()
    
def send_file_list (sock):
    file_list = '&'.join(FILES)
    sock.send(file_list)
    # print file_list
    
def get_files():
    number_of_file = input("Enter the number of files you want to send: ")
    number_of_file = number_of_file + 1
    for i in range(1, number_of_file):
        while 1:
            file = raw_input("File Location: ")
            if os.path.isfile(file):
                FILES.append(file)
                break
            else:
                print "File not found"

def main ():
    global PORT
    global CLIENT
    global TO_SEND
    global FILES
    # look_for_clients()
    t = threading.Thread(target=look_for_clients)
    t.setDaemon(True)
    t.start()
    
    get_files()
    
    while True:
        print "Searching for clients"
        time.sleep(5)
        if not CLIENT:
            ch = raw_input ("Failed to retrive clients, retry (Y,n): ")
            if ch == 'Y':
                continue
            else:
                sys.exit()
            
        print CLIENT
        send_to = raw_input('Enter the hostname to want to send to: ')
        try:
            ip = CLIENT[send_to]
            break
        except:
            print "Hostname not found, retrying."
    TO_SEND = send_to
    initiate_client(CLIENT[send_to])
    TO_SEND = CLIENT[send_to]
    '''
    initiate_client('192.168.1.4')                                     
    TO_SEND = '192.168.1.4'
    '''
    serv = socket(AF_INET, SOCK_STREAM)
    serv.bind(('', 4000))
    serv.listen(5)
    while True:
        conn, addr = serv.accept()
        print "Received a request."
        if addr[0] == TO_SEND:
            print "Client varified"
            send_file_list(conn)                                             # send file list
            for i in FILES:
                time.sleep(2)
                print "Starting Send Over process"
                file = conn.recv(1024)                                       # receive file loc to send
                if file in FILES:
                    send_over(file, conn)
                    file = None
                # serv.shutdown(SHUT_RDWR)
                serv.close()
                # serv = socket(AF_INET, SOCK_STREAM)
                # serv.bind(('', 4000))
                # serv.listen(5)
            break
        else:
            break
        
    serv.close()
    
if __name__ == '__main__':
    main()
    
