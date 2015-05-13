import socket   #for sockets
import sys  #for exit
import struct
import numpy as np
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
    id = struct.unpack('B', payload[1:2])[0]
    return id

def get_zoom_from_payload(payload):
    zoom = struct.unpack('B', payload[0:1])[0]
    return zoom

def get_map_from_payload(payload):
    map = list()

    for pad in range(61, 511):
        map.append(struct.unpack('B', payload[pad:pad + 1])[0])

    return map

def parse_map_from_server(map):
    map_matrix = np.zeros((15, 15))
    index = 0
    i = 0
    j = 0
    for c in map:
        #ignoring first byte
        if index % 2 == 0:
            index = index+1
            continue
        else:
            map_matrix.itemset((i, j), int(c))
            if j < 14:
                j = j+1
            else:
                i = i+1
                j = 0
            index = index+1


    return map_matrix

def begin_streaming(s, HOST, PORT, drone):
    #first request
    input("Press ENTER to begin streaming")
    params = PayloadProperties()
    params.port = PORT
    params.id = drone.id
    params.zoom = drone.zoom
    payload = ClientPayload()
    payload.add_params(params)
    payload.add_drone_xpos(drone.dx)
    payload.add_drone_ypos(drone.dy)
    payload.add_drone_zpos(drone.dz)
    payload.add_drone_land_info(drone.islanding)

    while 1:
        try:
            #Send payload
            s.sendto(payload.payload, (HOST, PORT))

            #Recebe Payload do server
            d = s.recvfrom(512)
            reply = d[0]
            addr = d[1]

            if drone.islanding:
                return 1

            id = get_droneid_from_payload(reply)
            zoom = get_zoom_from_payload(reply)
            map = get_map_from_payload(reply)

            print("Server reply:")
            print("Drone id: "+str(id))
            print("Drone zoom: "+str(zoom))
            #print("Drone Map: "+str(map))

            map_matrix = parse_map_from_server(map)

            print(map_matrix)

            payload = ClientPayload()

            if drone.zoom > 1:
                setores = drone.addPontos(map_matrix)
                payload = drone.chooseDirection(setores)
            else:
                payload = drone.testePouso(map_matrix)


            if not drone.islanding:
                input("Press enter to send next payload")

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

    begin_streaming(s, HOST, PORT, drone)

    s.close()

if __name__ == "__main__":
    main()