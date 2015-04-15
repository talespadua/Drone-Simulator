import socket
import sys
import configparser
from bs4 import BeautifulSoup
from Map import Map
from payload import ServerPayload, PayloadProperties
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

#keep talking with the drone
def begin_listening(socket, PORT):
    print("Server is listening on port " + PORT.__str__() + "...")
    while 1:
        # receive data from drone (data, addr)
        payload = ServerPayload()
        d = socket.recvfrom(512)
        data = d[0]
        addr = d[1]

        print("The data received is: " + data)

        input("Press to continue")

        payload.add_drone_id(10)
        payload.add_drone_zoom(10)
        payload.add_drone_map("sherolero")
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

    begin_listening(s, PORT)
    s.close()

if __name__ == "__main__":
    main()