import socket   #for sockets
import sys  #for exit

import configparser

from drone import Drone

config = configparser.RawConfigParser()
config.read('settings.cfg')

HOST = config.get('settings', 'host')
PORT = int(config.get('settings', 'port'));

drone = Drone()
drone.port = PORT

# create dgram udp socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error:
    print('Failed to create socket')
    sys.exit()

# try:
#     s.bind((HOST, PORT))
# except socket.error as msg:
#     print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
#     sys.exit()
 
while 1:
    msg = bytes(input('Enter message to send : '), encoding="UTF-8")

    #Enviar payload do client

    #setores = drone.addPontos()
    #msg = drone.chooseDirection(setores)
     
    try:
        #Set the whole string

        s.sendto(msg, (HOST, PORT))
         
        # receive data from client (data, addr)
        #Recebe Payload do server
        d = s.recvfrom(512)
        reply = d[0]
        addr = d[1]
         
        print('Server reply : ' + str(reply)[1:])
     
    except socket.error as msg:
        print('Error Code : ' + str(msg[0])[1:] + ' Message ' + msg[1])
        sys.exit()