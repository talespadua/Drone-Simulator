__author__ = 'tales.cpadua'
import struct
import sys
import codecs

class PayloadProperties():
    pass

#Payload server -> drone
class ServerPayload():
    def __init__(self):
        self.payload = bytearray(512)
        #Mapa de pontos

    def add_drone_id(self, id):
        struct.pack_into('B', self.payload, 0, int(id))

    def add_drone_zoom(self, zoom):
        struct.pack_into('B', self.payload, 23, int(zoom))

    def add_message_type(self, type):
        struct.pack_into('B', self.payload, 1, int(type))

    def add_message_id(self, id):
        struct.pack_into('B', self.payload, 2, int(id))

    #TODO: implement turn and movement
    def add_normal_wind(self, value):
        struct.pack_into('>i', self.payload, 3, int(value))

    def add_frontal_wind(self, value):
        struct.pack_into('>i', self.payload, 7, int(value))

    def add_binormal_wind(self, value):
        struct.pack_into('>i', self.payload, 11, int(value))

    def add_gps_posx(self, posx):
        struct.pack_into('>I', self.payload, 15, int(posx))

    def add_gps_posy(self, posy):
        struct.pack_into('>I', self.payload, 19, int(posy))

    def add_drone_map(self, map):
        #sherolero = bytearray(map, "utf-8")
        #struct.pack_into('450s', self.payload, 61, sherolero)

        count = 61

        for val in map:
            struct.pack_into('B', self.payload, count, int(val))
            count += 1

    def pack_payload(self):
        return bytes(self.elements)

    def print_payload_size(self):
        print(sys.getsizeof(self.payload))
        print(struct.calcsize('BB'))

    def print_payload(self, beg, end):
        print(self.payload[beg:end])


#Payload drone -> server
#TODO: Implement new method on udp_client
class ClientPayload:
    def __init__(self):
        self.payload = bytearray(512)

    def add_drone_normal_vector(self, value):
        struct.pack_into('>i', self.payload, 8, int(value))

    def add_drone_frontal_vector(self, value):
        struct.pack_into('>i', self.payload, 12, int(value))

    def add_drone_binormal_vector(self, value):
        struct.pack_into('>i', self.payload, 16, int(value))

    #TODO: Waiting committee. But probably in position 20
    def add_drone_land_info(self, islanded):
        struct.pack_into('?', self.payload, 20, islanded)

    def add_port(self, port):
        struct.pack_into('>I', self.payload, 0, int(port))

    def add_id(self, id):
        struct.pack_into('B', self.payload, 4, int(id))

    def add_msg_id(self, id):
        struct.pack_into('B', self.payload, 5, int(id))

    def add_msg_type(self, msg_type):
        struct.pack_into('B', self.payload, 6, int(msg_type))

    def add_zoom(self, zoom):
        struct.pack_into('B', self.payload, 7, int(zoom))

    def get_payload(self):
        return self.payload