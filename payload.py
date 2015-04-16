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
        struct.pack_into('B', self.payload, 1, int(zoom))

    def add_drone_map(self, map):
        sherolero = bytearray(map, "utf-8")
        struct.pack_into('450s', self.payload, 61, sherolero)

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

    def add_drone_xpos(self, xpos):
        struct.pack_into('>i', self.payload, 6, int(xpos))

    def add_drone_ypos(self, ypos):
        struct.pack_into('>i', self.payload, 10, int(ypos))

    def add_drone_zpos(self, zpos):
        struct.pack_into('>i', self.payload, 14, int(zpos))

    def add_drone_land_info(self, islanded):
        struct.pack_into('?', self.payload, 18, islanded)

    def add_params(self, params):
<<<<<<< HEAD
        struct.pack_into('>IBBiii?',
=======
        struct.pack_into('IBB',
>>>>>>> 2b303cfa03d7125787c0a19398c01ab603e46667
                         self.payload,
                         0,
                         params.port,
                         params.id,
                         params.zoom)

    def get_payload(self):
        return self.payload