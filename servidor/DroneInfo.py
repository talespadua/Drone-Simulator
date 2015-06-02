__author__ = 'tales.cpadua'

class DroneInfo:
    def __init__(self, drone_id, pos_x, pos_y, pos_z):
        self.drone_id = drone_id
        self.payload_queue = []
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.pos_z = pos_z