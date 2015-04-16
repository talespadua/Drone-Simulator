import socket   #for sockets
import sys  #for exit
import struct

import configparser
from payload import ClientPayload, PayloadProperties
from drone import Drone #WHAT

def get_config(config_file):
    config = configparser.RawConfigParser()
    config.read(config_file)
    return config

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')
        return s
    except socket.error as msg:
        print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

def get_droneid_from_payload(payload):
    id = struct.unpack('B', payload[0:1])[0]
    return id

def get_zoom_from_payload(payload):
    zoom = struct.unpack('B', payload[1:2])[0]
    return zoom

def get_map_from_payload(payload):
    map = struct.unpack('100s', payload[61:161])[0]
    return map

def begin_streaming(s, HOST, PORT):

    #first request
    input("Press ENTER to begin streaming")
    params = PayloadProperties()
    params.port = PORT
    params.id = 1
    params.zoom = 10
    params.dx = 0
    params.dy = 0
    params.dz = 0
    payload = ClientPayload()
    payload.add_params(params)

    while 1:
        try:
            #Send payload
            s.sendto(payload.payload, (HOST, PORT))

            #Recebe Payload do server
            d = s.recvfrom(512)
            reply = d[0]
            addr = d[1]

            id = get_droneid_from_payload(reply)
            zoom = get_zoom_from_payload(reply)
            map = get_map_from_payload(reply)

            print("Server reply:")
            print("Drone id: "+str(id))
            print("Drone zoom: "+str(zoom))
            print("Drone Map: "+str(map))


            input("Press enter to sent next payload")
        except socket.error as msg:
            print('Error Code : ' + str(msg[0])[1:] + ' Message ' + msg[1])
            sys.exit()

def main():
    config = get_config("settings.cfg")

    HOST = config.get('settings', 'host')
    PORT = int(config.get('settings', 'port'))

    s = create_socket()

    drone = Drone()
    drone.port = PORT

    begin_streaming(s, HOST, PORT)


if __name__ == "__main__":
    main()