__author__ = 'tales.cpadua'
import struct
import sys

class PayloadProperties():
    pass

#Payload server -> client
class ServerPayload():
    def __init__(self, params):
        self.elements = ""
        self.droneID = params.id
        self.zoom = params.zoom
        #Mapa de pontos

        self.payload = struct.pack('BB', self.droneID, self.zoom)

    def pack_payload(self):
        return bytes(self.elements)

    def print_payload_size(self):
        print(sys.getsizeof(self.payload))
        print(struct.calcsize('BB'))

#Payload client -> server
class ClientPayload():
    def __init__(self, params):
        self.port = params.port
        self.id = params.id
        self.zoom = params.zoom
        self.dx = params.dx
        self.dy = params.dy
        self.dz = params.dz

        self.payload = struct.pack('IBBiii')