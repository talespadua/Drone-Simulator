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

    #TODO: implement commented line if changes stay
    def add_drone_zoom(self, zoom):
        struct.pack_into('B', self.payload, 1, int(zoom))
        #struct.pack_into('B', self.payload, 23, int(zoom))

    #TODO: New Method
    def add_message_type(self, type):
        struct.pack_into('B', self.payload, 1, int(type))

    #TODO: New Method
    def add_message_id(self, id):
        struct.pack_into('B', self.payload, 2, int(id))

    #TODO: New Method
    def add_normal_wind(self, value):
        struct.pack_into('>i', self.payload, 3, int(value))

    #TODO: New Method
    def add_frontal_wind(self, value):
        struct.pack_into('>i', self.payload, 7, int(value))

    #TODO: New Method
    def add_binormal_wind(self, value):
        struct.pack_into('>i', self.payload, 11, int(value))

    #TODO: New Method
    def add_gps_posx(self, posx):
        struct.pack_into('>I', self.payload, 15, int(posx))

    #TODO: New Method
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
class ClientPayload:
    def __init__(self):
        self.payload = bytearray(512)

    #TODO: Next 3 methdos for pos x z and y DEPRECATED
    def add_drone_xpos(self, xpos):
        struct.pack_into('>i', self.payload, 6, int(xpos))

    def add_drone_ypos(self, ypos):
        struct.pack_into('>i', self.payload, 10, int(ypos))

    def add_drone_zpos(self, zpos):
        struct.pack_into('>i', self.payload, 14, int(zpos))

    #TODO: Next 3 methdos is according to last committee agreement, but order of vectors not clear. Need to implement
    def add_drone_normal_vector(self, value):
        struct.pack_into('>i', self.payload, 8, int(value))

    def add_drone_frontal_vector(self, value):
        struct.pack_into('>i', self.payload, 12, int(value))

    def add_drone_binormal_vector(self, value):
        struct.pack_into('>i', self.payload, 16, int(value))

    #TODO: Deprecated. Talk with committee to know where this info is going
    def add_drone_land_info(self, islanded):
        struct.pack_into('?', self.payload, 18, islanded)

    #TODO: implement method
    def add_port(self, port):
        struct.pack_into('>I', self.payload, 0, int(port))

    #TODO: implement method
    def add_id(self, id):
        struct.pack_into('B', self.payload, 4, int(id))

    #TODO: implement method
    def add_msg_id(self, id):
        struct.pack_into('B', self.payload, 5, int(id))

    #TODO: implement method
    def add_msg_type(self, msg_type):
        struct.pack_into('B', self.payload, 6, int(msg_type))

    #TODO: implement method
    def add_zoom(self, zoom):
        struct.pack_into('B', self.payload, 7, int(zoom))

    #TODO: deprecated in new document
    def add_params(self, params):
        struct.pack_into('IBB',
                         self.payload,
                         0,
                         params.port,
                         params.id,
                         params.zoom)

    def get_payload(self):
        return self.payload