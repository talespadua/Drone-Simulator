import socket
import sys
import configparser
from bs4 import BeautifulSoup
from Map import Map
from payload import ServerPayload
import functions as f
import struct
from random import randint
from servidor.DroneInfo import DroneInfo
import math

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
    port = struct.unpack('>I', payload[0:4])[0]
    return port


def get_drone_id_from_payload(payload):
    drone_id = struct.unpack('B', payload[4:5])[0]
    return drone_id


def get_message_type(payload):
    msg_type = struct.unpack('B', payload[6:7])[0]
    return msg_type


def get_message_id(payload):
    msg_id = struct.unpack('B', payload[5:6])[0]
    return msg_id


def get_zoom_from_payload(payload):
    zoom = struct.unpack('B', payload[7:8])[0]
    return zoom


def get_normal_from_payload(payload):
    x_pos = struct.unpack('>i', payload[16:20])[0]
    return x_pos


def get_frontal_from_payload(payload):
    z_pos = struct.unpack('>i', payload[12:16])[0]
    return z_pos


def get_rotation_from_payload(payload):
    y_pos = struct.unpack('>i', payload[8:12])[0]
    return y_pos


def parse_drone_map_to_string(x, z, zoom, mapa):
    map_matrix = f.getArrayToDrone(x, z, zoom, mapa.map_array, mapa.x_size, mapa.z_size)
    map_type_matrix = f.getArrayToDrone(x, z, zoom, mapa.type_array, mapa.x_size, mapa.z_size)
    # map_string = ''
    # for i in range(15):
    #         for j in range(15):
    #             map_string = map_string + "0" + str(int(map_matrix[i][j]))

    map_list = list()

    for i in range(15):
        for j in range(15):
            map_list.append(map_type_matrix[i][j])
            map_list.append(map_matrix[i][j])

    return map_list


def get_drone(drone_list, drone_id):
    for d in drone_list:
        if d.drone_id == drone_id:
            return d
    return None


def get_drone_model_tcp(drone_model_number):
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12345                 # Reserve a port for your service.
    s.bind((host, port))        # Bind to the port
    file = open('DroneModel_'+str(drone_model_number)+'.x3d', 'wb')
    s.listen(5)                 # Now wait for client connection.
    while True:
        c, addr = s.accept()     # Establish connection with client.
        print('Got connection from', addr)
        print("Receiving...")
        l = c.recv(1024)
        while (l):
            print("Receiving...")
            file.write(l)
            l = c.recv(1024)
        file.close()
        print("Done Receiving")
        c.close()                # Close the connection
        s.close()
        return


def check_area_collision(do, dt):
    dist = math.sqrt((do.pos_x - dt.pos_x)**2 + (do.pos_y - dt.pos_y)**2 + (do.pos_z - dt.pos_z)**2)
    return dist


# def check_drone_proximity(drone, drone_list):
#     list_len = len(drone_list)
#     if list_len < 2:
#         return None
#
#     for d in drone_list:
#         dist = check_area_collision(drone, d)
#         if dist < 150:
#
#     starting_point = 0
#     while starting_point < list_len - 1:
#         i = starting_point + 1
#         while i < list_len:
#             if check_area_collision(drone_list[starting_point], drone_list[i]):
#                 return drone_list[starting_point], drone_list[i]
#             i += 1
#         starting_point += 1
#     return None


#keep talking with the drone
def begin_listening(sock, port, server_map, config):
    print("Server is listening on port " + port.__str__() + "...")

    drone_list = []

    drone_model_number = int(config.get('settings', 'drone_model_number'))

    normal_wind = 0
    frontal_wind = randint(-10, 10)
    binormal_wind = randint(-10, 10)

    if frontal_wind > 5 or frontal_wind < 5:
        #Uma segunda rolagem concentra resultados numa margem pequena. (Aprox. 75% de chance de estar entre 0 e 5)
        frontal_wind = randint(-10, 10)
    if binormal_wind > 5 or binormal_wind < 5:
        #Uma segunda rolagem concentra resultados numa margem pequena. (Aprox. 75% de chance de estar entre 0 e 5)s
        binormal_wind = randint(-10, 10)

    while 1:
        # receive data from drone (data, addr)
        payload = ServerPayload()
        d = sock.recvfrom(512)
        data = d[0]
        addr = d[1]

        print("The data received is: " + str(data))

        #PARSE DATA FROM DRONE
        drone_id = get_drone_id_from_payload(data)

        drone = get_drone(drone_list, drone_id)

        msg_type = get_message_type(data)
        msg_id = get_message_id(data)

        if msg_type == 1:
            print("Drone with ID " + drone.drone_id + "landed")
            drone_list.remove(drone)
            msg_type = 3
            payload.add_drone_id(drone_id)
            payload.add_message_type(msg_type)
            payload.add_message_id(msg_id)

            sock.sendto(payload.payload, drone.addr)
            continue

        drone_port = get_port_from_payload(data)

        if drone is None:
            pos_x = randint(10, server_map.x_size - 11)
            pos_y = 80
            pos_z = randint(10, server_map.z_size - 11)
            drone = DroneInfo(drone_id, pos_x, pos_y, pos_z, addr)
            drone_list.append(drone)

            payload.add_drone_id(drone.drone_id)
            payload.add_message_id(msg_id)
            payload.add_message_type(4)

            sock.sendto(payload.payload, drone.addr)

            get_drone_model_tcp(drone_model_number)

            payload.add_message_type(0)

            drone_model_number += 1
            config.set('settings', 'drone_model_number', str(drone_model_number))
            with open("settings.cfg", 'w') as configfile:
                config.write(configfile)

            sock.sendto(payload.payload, drone.addr)
            continue

        zoom = get_zoom_from_payload(data)
        #Last drone movement
        normal_mov = get_normal_from_payload(data)
        frontal_mov = get_frontal_from_payload(data)
        rotation = get_rotation_from_payload(data)

        drone_pos = f.convertFrontalMovementIntoXZ(rotation, frontal_mov)

        collision = f.verifyCollision(drone.pos_x, drone.pos_z, drone.pos_x + drone_pos[0], drone.pos_y + normal_mov,
                                      drone.pos_z + drone_pos[1], server_map)

        drone.pos_y += normal_mov
        drone.pos_x += drone_pos[0]
        drone.pos_z += drone_pos[1]

        # prox_drones = check_drone_proximity(drone, drone_list)
        #
        # if prox_drones is not None:
        #     msg_type = 2

        if collision == -1:
            print("Drone with ID " + str(drone.drone_id) + "Collided")
            drone_list.remove(drone)
            msg_type = 3
            payload.add_drone_id(drone_id)
            payload.add_message_type(msg_type)
            payload.add_message_id(msg_id)

            sock.sendto(payload.payload, drone.addr)
            continue

        #TODO: implement drone-to-drone communication
        map_str = parse_drone_map_to_string(drone.pos_x, drone.pos_z, zoom, server_map)

        payload.add_drone_id(drone_id)
        payload.add_message_type(msg_type)
        payload.add_message_id(msg_id)

        payload.add_normal_wind(normal_wind)
        payload.add_frontal_wind(frontal_wind)
        payload.add_binormal_wind(binormal_wind)

        payload.add_gps_posx(drone.pos_x)
        payload.add_gps_posz(drone.pos_z)

        payload.add_drone_zoom(zoom)
        payload.add_drone_map(map_str)

        #payload.print_payload(55, 80)
        #payload.print_payload_size()
        sock.sendto(payload.payload, drone.addr)


def main():
    config = get_config('settings.cfg')
    soup = load_to_soup('../mapas/EasyMap.xml')
    soup_map = Map(soup)

    # Datagram (udp) socket
    host = config.get('settings', 'host')  # Symbolic name meaning all available interfaces
    port = int(config.get('settings', 'port'))  # Arbitrary non-privileged port

    s = create_socket()
    bind_socket(s, host, port)

    begin_listening(s, port, soup_map, config)
    s.close()


if __name__ == "__main__":
    main()