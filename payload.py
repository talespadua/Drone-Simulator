__author__ = 'tales.cpadua'
import struct
import sys

class PayloadProperties():
    pass

class ServerPayload():
    def __init__(self, params):
        self.elements = ""
        self.droneID = params.id
        self.zoom = params.zoom

        self.payload = struct.pack('BB', self.droneID, self.zoom)

    def pack_payload(self):
        return bytes(self.elements)

    def print_payload_size(self):
        print(sys.getsizeof(self.payload))
        print(struct.calcsize('BB'))

class ClientPayload():
    pass