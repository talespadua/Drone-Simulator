import socket
import sys
import configparser
from bs4 import BeautifulSoup
from Map import Map
from payload import ServerPayload, PayloadProperties
import functions as f
import struct
import numpy as np
from drone.drone import Drone

#Setting up config parser
def get_config(config_file):
    config = configparser.RawConfigParser()
    config.read(config_file)
    return config

#Load X3D map to soup
def load_to_soup(map_path):
    try:
        soup = BeautifulSoup(open(map_path))
    except:
        print("Error loading map")
        sys.exit()
    return soup

def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created')
        return s
    except socket.error as msg:
        print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

def bind_socket(socket, HOST, PORT):
    # Bind socket to local host and port
    try:
        socket.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Socket bind complete')


def get_port_from_payload(payload):
    port = struct.unpack('I', payload[0:4])[0]
    return port

def get_droneid_from_payload(payload):
    id = struct.unpack('B', payload[4:5])[0]
    return id

def get_zoom_from_payload(payload):
    zoom = struct.unpack('B', payload[5:6])[0]
    return zoom

def get_x_position_from_payload(payload):
    x_pos = struct.unpack('>i', payload[6:10])[0]
    return x_pos

def get_y_position_from_payload(payload):
    y_pos = struct.unpack('>i', payload[10:14])[0]
    return y_pos

def get_z_position_from_payload(payload):
    z_pos = struct.unpack('>i', payload[14:18])[0]
    return z_pos

def get_islanded_from_payload(payload):
    islanded = struct.unpack('?', payload[18:19])[0]
    return islanded

def parse_drone_map_to_string(x, z, zoom, mapa):
    map_matrix = f.getArrayToDrone(x, z, zoom, mapa.map_array)
    map_string = ''
    for i in range(15):
            for j in range(15):
                map_string = map_string + "0" + str(int(map_matrix[i][j]))
    return map_string

#keep talking with the drone
def begin_listening(socket, PORT, map):
    print("Server is listening on port " + PORT.__str__() + "...")
    soup = load_to_soup('../mapas/DotaMap.xml')
    oldX = 10
    oldZ = 10
    while 1:
        # receive data from drone (data, addr)
        payload = ServerPayload()
        d = socket.recvfrom(512)
        data = d[0]
        addr = d[1]

        print("The data received is: " + str(data))

        #PARSE DATA FROM DRONE
        drone_port = get_port_from_payload(data)
        zoom = get_zoom_from_payload(data)
        id = get_droneid_from_payload(data)
        x_pos = get_x_position_from_payload(data)
        y_pos = get_y_position_from_payload(data)
        z_pos = get_z_position_from_payload(data)
        islanded = get_islanded_from_payload(data)

        print("zoom is :" + str(zoom))
        print("id is : "+str(id))
        print("Drone positions: ")
        print("x: " + str(x_pos))
        print("y: " + str(y_pos))
        print("z: " + str(z_pos))
        print("Landed: " + str(islanded))

        colision = f.verifyCollision(oldX, oldZ, x_pos, y_pos, z_pos, map)
        oldX = x_pos
        oldZ = z_pos

        if colision == -1:
            return 0

        if islanded:
            return 1

        map_str = parse_drone_map_to_string(x_pos, z_pos, zoom, map)

        payload.add_drone_id(10)
        payload.add_drone_zoom(zoom)

        payload.add_drone_map(map_str)
        payload.add_drone_id(zoom)
        payload.add_drone_zoom(id)

        #payload.print_payload(55, 80)
        #payload.print_payload_size()
        socket.sendto(payload.payload, addr)

def main():
    config = get_config('settings.cfg')
    soup = load_to_soup('../mapas/DotaMap.xml')
    map = Map(soup)

    # Datagram (udp) socket
    HOST = config.get('settings', 'host')   # Symbolic name meaning all available interfaces
    PORT = int(config.get('settings', 'port')) # Arbitrary non-privileged port

    s = create_socket()
    bind_socket(s, HOST, PORT)

    result = begin_listening(s, PORT, map)
    s.close()

    if result == 1:
        print("O drone pousou adequadamente. Encerrando simulação")
    else:
        print("O Drone colidiu. Abortando simulação")

if __name__ == "__main__":
    main()