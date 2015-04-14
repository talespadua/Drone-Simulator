import socket   #for sockets
import sys  #for exit

import configparser

config = configparser.RawConfigParser()
config.read('settings.cfg')

# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

host = config.get('settings', 'host')
port = int(config.get('settings', 'port'));
 
while 1:
    msg = bytes(input('Enter message to send : '), encoding="UTF-8")
     
    try:
        #Set the whole string
        s.sendto(msg, (host, port))
         
        # receive data from client (data, addr)
        d = s.recvfrom(512)
        reply = d[0]
        addr = d[1]
         
        print('Server reply : ' + str(reply)[1:])
     
    except socket.error as msg:
        print('Error Code : ' + str(msg[0])[1:] + ' Message ' + msg[1])
        sys.exit()