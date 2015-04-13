import socket
import sys
import configparser

config = configparser.RawConfigParser()
config.read('settings.cfg')

HOST = config.get('settings', 'host')   # Symbolic name meaning all available interfaces
PORT = int(config.get('settings', 'port')) # Arbitrary non-privileged port
 
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
    data = d[0]
    addr = d[1]
     
    if not data: 
        break
     
    reply = 'OK...' + str(data)[1:]
    
    s.sendto(bytes(reply, encoding="UTF-8") , addr)
    print('Message [' + addr[0] + ':' + str(addr[1])[1:] + '] - ' + str(data)[1:].strip())
     
s.close()