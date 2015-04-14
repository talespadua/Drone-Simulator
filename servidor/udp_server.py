import socket
import sys
import configparser
import numpy as np
from bs4 import BeautifulSoup

config = configparser.RawConfigParser()
config.read('settings.cfg')

HOST = config.get('settings', 'host')   # Symbolic name meaning all available interfaces
PORT = int(config.get('settings', 'port')) # Arbitrary non-privileged port
#
# with open('../mapas/DotaMap.xml', 'r') as map:
try:
    soup = BeautifulSoup(open('../mapas/DotaMap.xml'))
except:
    print("erro")


print(soup)
# Datagram (udp) socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')
except socket.error as msg:
    print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
 
 
# Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
     
print('Socket bind complete')
 
#now keep talking with the client
while 1:
    # receive data from client (data, addr)
    d = s.recvfrom(512)
    data = d[0].decode('utf-8')
    addr = d[1]

    if not data:
        print("Size of message is: " + str(sys.getsizeof(data)))
        print("No data received for package in address " + str(addr))
        s.sendto(bytes("No data received", encoding="UTF-8"), addr)
        continue
     
    reply = 'OK...' + data[1:]

    print("payload was " + str(d))
    print("Size of message is: " + str(sys.getsizeof(data)))

    s.sendto(bytes(reply, encoding="UTF-8"), addr)
    print('Message [' + addr[0] + ':' + str(addr[1])[1:] + '] - ' + data[1:].strip())
     
s.close()