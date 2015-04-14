__author__ = 'tales.cpadua'
import numpy as np

class Map:
    def __init__(self, soup):
        #Loading X3D parameters to python variables
        self.map_tag = soup.find('elevationgrid')
        self.map_nodes = self.map_tag['height'] # y pointss
        self.x_size = int(self.map_tag['xdimension'])
        self.z_size = int(self.map_tag['zdimension'])

        self.map_array = np.zeros((self.x_size, self.z_size)) #matrix of y values. Indexes are X and Y values

        print("Map x value is: " + str(self.x_size))
        print("Map z value is: " + str(self.z_size))
        temp = ""
        i = 0
        j = 0

        #Filling X3D map to matrix
        for c in self.map_nodes:
            if c is '\n':
                self.map_array[i][j] = int(temp)
                temp = ""
                i = i+1
                j = 0
                continue
            if c is ' ':
                if temp is "":
                    continue
                self.map_array[i][j] = int(temp)
                temp = ""
                j = j+1
                continue

            temp = temp+c
        print("Map load successful")

    def print_map(self):
        print("Matrix is: ")
        for x in range(self.x_size):
            for z in range(self.z_size):
                print(self.map_array[x][z])