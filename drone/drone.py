from random import random, randint

class ponto:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class drone:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		self.bsRaio = 5
		self.mapa = list()
		self.pernas = [[8, 2, 8], [3, 2, 5], [7, 2, 5]]
		self.zoom = 1
		#self.estado = 1

	def moveBy(self, x, y, z):
		self.x += x
		self.y += y
		self.z += z

class mapa:
	def __init__(self, hMin, hMax, larg, comp):
		self.mapa = list()

		for x in range(larg):
			self.mapa.append(list())

			for z in range(comp):
				self.mapa[x].append(randint(hMin, hMax))




#mapa(TEMP)
mapaLarg = 50
mapaComp = 50
mapa = mapa(0, 10, mapaLarg, mapaComp)

#drone(DEF)
drone = drone(randint(0, 99), randint(0, 99), randint(0, 99))

print "DronePos = %d %d %d" %(drone.x, drone.y, drone.z)

testDestino = [randint(0, 99), randint(0, 10), randint(0, 99)]

print "Destino: %d %d %d" %(testDestino[0], testDestino[1], testDestino[2])

drone.moveBy(testDestino[0] - drone.x, testDestino[1] - drone.y, testDestino[2] - drone.z)

print "DronePos = %d %d %d" %(drone.x, drone.y, drone.z)