from random import random, randint
from fpformat import fix

#mapa(TEMP)
hMin = 0
hMax = 5

mapa = list()

for x in range(100):
	mapa.append(list())

	for z in range(100):
		r = 0 #random() * hMax\
		mapa[x].append(r)

		#print mapa[x][z]

#drone(DEF)
droneBSRaio = 5
droneTPAlt = -3
#droneDiscoAlt = 
#droneDiscoRaio = 

droneEstado = 1
droneMapa = list()

droneX = float(randint(1, 100))
droneZ = float(randint(1, 100))
droneY = float(35)

dronePernas = [[8, 2, 8], [3, 2, 5], [7, 2, 5]]

print "DronePos = %d %d %d" %(droneX, droneY, droneZ)

droneVel = list()

testDestino = [randint(0, 100), randint(0, 100), randint(0, 100)]

print "Destino: %d %d %d" %(testDestino[0], testDestino[1], testDestino[2])

tempoMov = 25

droneVel.append((testDestino[0] - droneX) / tempoMov)
droneVel.append((testDestino[1] - droneY + 3) / tempoMov)
droneVel.append((testDestino[2] - droneZ) / tempoMov)

print "Vel: %.2f %.2f %.2f" %(droneVel[0], droneVel[1], droneVel[2])

for i in range(tempoMov):
	droneX = droneX + droneVel[0]
	droneY = droneY + droneVel[1]
	droneZ = droneZ + droneVel[2]

	print "Pos em t = %d: %.2f %.2f %.2f" %(i + 1, droneX, droneY, droneZ)