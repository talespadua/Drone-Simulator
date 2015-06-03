import socket
import sys
import struct
import numpy as np
import configparser
from payload import ClientPayload, PayloadProperties
from drone import Drone #WHAT


def get_config(config_file):
    config = configparser.RawConfigParser()
    config.read(config_file, encoding='utf-8')
    return config


def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
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
        return False
    print('Socket bind complete')
    return True


def get_drone_id_from_payload(payload):
    drone_id = struct.unpack('B', payload[0:1])[0]
    print("Drone ID: %d" %(drone_id))
    return drone_id


def get_message_type(payload):
    msg_type = struct.unpack('B', payload[1:2])[0]
    return msg_type


def get_message_id(payload):
    msg_id = struct.unpack('B', payload[2:3])[0]
    return msg_id


def get_normal_wind(payload):
    normal_wind = struct.unpack('>i', payload[3:7])[0]
    return normal_wind


def get_frontal_wind(payload):
    frontal_wind = struct.unpack('>i', payload[7:11])[0]
    return frontal_wind


def get_binormal_wind(payload):
    binormal_wind = struct.unpack('>i', payload[11:15])[0]
    return binormal_wind


def get_gps_pos_x(payload):
    gps_posx = struct.unpack('>I', payload[15:19])[0]
    return gps_posx


def get_gps_pos_z(payload):
    gps_posz = struct.unpack('>I', payload[19:23])[0]
    return gps_posz


def get_zoom_from_payload(payload):
    zoom = struct.unpack('B', payload[23:24])[0]
    return zoom


def get_map_from_payload(payload):
    server_map = list()

    for pad in range(61, 511):
        server_map.append(struct.unpack('B', payload[pad:pad + 1])[0])

    return server_map

def parse_map_from_server(server_map):
    map_matrix = np.zeros((15, 15))
    type_matrix = np.zeros((15, 15))
    index = 0
    i = 0
    j = 0
    for c in server_map:
        #ignoring first byte
        if index % 2 == 0:
            type_matrix.itemset((i, j), int(c))
            index += 1
            continue
        else:
            map_matrix.itemset((i, j), int(c))
            if j < 14:
                j += 1
            else:
                i += 1
                j = 0
            index += 1
    return map_matrix


def transfer_drone_model():
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    port = 12345                 # Reserve a port for your service.

    s.connect((host, port))
    file = open('DroneModel.x3d', 'rb')
    print('Sending...')
    l = file.read(1024)
    while (l):
        print('Sending...')
        s.send(l)
        l = file.read(1024)
    file.close()
    print("Done Sending")
    s.shutdown(socket.SHUT_WR)
    s.close()


def begin_streaming(s, host, port, drone):
    #first request
    drone_id = drone.drone_id
    zoom = drone.zoom
    msg_id = 0
    msg_type = 0
    input("Press ENTER to begin streaming")

    first_round = True

    payload = ClientPayload()

    payload.add_port(drone.port)
    payload.add_drone_id(drone_id)

    payload.add_msg_id(msg_id)
    payload.add_msg_type(msg_type)
    payload.add_zoom(zoom)

    #0, 0, 0 are initial values
    payload.add_drone_normal_vector(0)
    payload.add_drone_frontal_vector(0)
    payload.add_drone_rotation(0)

    while 1:
        try:
            #Send payload
            s.sendto(payload.payload, (host, port))

            #Recebe Payload do server
            d = s.recvfrom(512)
            reply = d[0]
            addr = d[1]

            msg_type = get_message_type(reply)
             #TODO: make sure msg type is checked first
            if msg_type == 4:
                transfer_drone_model()
                msg_type = 0
                d = s.recvfrom(512)
                reply = d[0]
                addr = d[1]

            if msg_type == 3:
                sys.exit()

            rcv_msg_id = get_message_id(reply)

            if first_round is True:
                wind_normal = get_normal_wind(reply)
                wind_frontal = get_frontal_wind(reply)
                wind_binormal = get_binormal_wind(reply)
                first_round = False

            server_map = get_map_from_payload(reply)

            gps_posx = get_gps_pos_x(reply)
            gps_posz = get_gps_pos_z(reply)

            print("Server reply:")
            print("Drone id: "+str(drone.drone_id))
            print("Msg type: "+str(msg_type))

            map_matrix = parse_map_from_server(server_map)
            #print(map_matrix)

            drone.addPontos(map_matrix)

            if drone.zoom > 1 or drone.flyingTime < 2:
                payload = drone.chooseDirection(payload)

            #Para não dar conflito com o modo de obter vento
            elif drone.zoom == 1 and drone.flyingTime > 2:
                payload = drone.testePouso(payload)

            # input("Press enter to send next payload")

            msg_id += 1

        except socket.timeout:
            s.sendto(payload.payload, (host, port))
            continue


def main():
    config = get_config("settings.cfg")

    host = config.get('settings', 'host')
    drone_port = int(config.get('settings', 'port_seed'))
    server_port = int(config.get('settings', 'server_port'))

    s = create_socket()

    while True:
        if bind_socket(s, host, drone_port):
            break
        else:
            drone_port += 1

    config.set('settings', 'port_seed', str(drone_port+1))
    with open("settings.cfg", 'w') as configfile:
        config.write(configfile)

    drone = Drone()
    drone.port = drone_port

    begin_streaming(s, host, server_port, drone)

    s.close()

if __name__ == "__main__":
    main()