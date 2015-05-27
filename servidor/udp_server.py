import socket
import sys
import configparser
from bs4 import BeautifulSoup
from Map import Map
from payload import ServerPayload, PayloadProperties
import functions as f
import struct
from random import randint
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
        print('Failed to create socket. Error Code : ' + str(msg) + ' Message ' + str(msg))
        sys.exit()


def bind_socket(sock, host, port):
    # Bind socket to local host and port
    try:
        sock.bind((host, port))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg) + ' Message ' + str(msg))
        sys.exit()
    print('Socket bind complete')


def get_port_from_payload(payload):
    port = struct.unpack('I', payload[0:4])[0]
    print(int(port))
    return port


def get_drone_id_from_payload(payload):
    drone_id = struct.unpack('B', payload[4:5])[0]
    print(int(drone_id))
    return drone_id

def get_zoom_from_payload(payload):
    zoom = struct.unpack('B', payload[7:8])[0]
    print(int(zoom))
    return zoom


def get_normal_from_payload(payload):
    x_pos = struct.unpack('>i', payload[8:12])[0]
    print(int(x_pos))
    return x_pos


def get_frontal_from_payload(payload):
    z_pos = struct.unpack('>i', payload[12:16])[0]
    print(int(z_pos))
    return z_pos


def get_binormal_from_payload(payload):
    y_pos = struct.unpack('>i', payload[16:20])[0]
    print(int(y_pos))
    return y_pos


def get_is_landed_from_payload(payload):
    is_landed = struct.unpack('?', payload[18:19])[0]
    return is_landed


def parse_drone_map_to_string(x, z, zoom, mapa):
    map_matrix = f.getArrayToDrone(x, z, zoom, mapa.map_array)

    # map_string = ''
    # for i in range(15):
    #         for j in range(15):
    #             map_string = map_string + "0" + str(int(map_matrix[i][j]))

    map_list = list()

    for i in range(15):
        for j in range(15):
            map_list.append(0)
            map_list.append(map_matrix[i][j])

    return map_list


#keep talking with the drone
def begin_listening(sock, port, server_map):
    print("Server is listening on port " + port.__str__() + "...")
    soup = load_to_soup('../mapas/DotaMap.xml')
    old_x = randint(10, server_map.x_size - 11)
    old_y = 80
    old_z = randint(10, server_map.z_size - 11)

    print("drone init: %d %d %d" %(old_x, old_y, old_z))

    while 1:
        # receive data from drone (data, addr)
        payload = ServerPayload()
        d = sock.recvfrom(512)
        data = d[0]
        addr = d[1]

        print("The data received is: " + str(data))

        #PARSE DATA FROM DRONE
        drone_port = get_port_from_payload(data)
        zoom = get_zoom_from_payload(data)
        drone_id = get_drone_id_from_payload(data)

        #Deprecated
        # x_pos = get_x_position_from_payload(data)
        # y_pos = get_y_position_from_payload(data)
        # z_pos = get_z_position_from_payload(data)

        #TODO: Implement landed calculation with new payload format
        normal_mag = get_normal_from_payload(data)
        frontal_mag = get_frontal_from_payload(data)
        binormal_mag = get_binormal_from_payload(data)

        print(normal_mag, binormal_mag, frontal_mag, drone_id, drone_port, zoom)

        is_landed = get_is_landed_from_payload(data)

        #Por hora, usando frontal=z, binormal=y, normal=x

        collision = f.verifyCollision(old_x, old_z, old_x + normal_mag, old_y + binormal_mag, old_z + frontal_mag, server_map)
        old_x += normal_mag
        old_y += binormal_mag
        old_z += frontal_mag

        if collision == -1:
            return 0

        if is_landed:
            return 1

        map_str = parse_drone_map_to_string(old_x, old_z, zoom, server_map)

        #TODO: implement new methods from server payload here
        payload.add_drone_map(map_str)
        payload.add_drone_id(zoom)
        payload.add_drone_zoom(drone_id)

        #payload.print_payload(55, 80)
        #payload.print_payload_size()
        sock.sendto(payload.payload, addr)
        return 0


def main():
    config = get_config('settings.cfg')
    soup = load_to_soup('../mapas/DotaMap.xml')
    soup_map = Map(soup)

    # Datagram (udp) socket
    host = config.get('settings', 'host')   # Symbolic name meaning all available interfaces
    port = int(config.get('settings', 'port'))  # Arbitrary non-privileged port

    s = create_socket()
    bind_socket(s, host, port)

    result = begin_listening(s, port, soup_map)
    s.close()

    if result == 1:
        print("O drone pousou adequadamente. Encerrando simulação")
    else:
        print("O Drone colidiu. Abortando simulação")

if __name__ == "__main__":
    main()