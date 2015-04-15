from random import randint
from payload import ClientPayload

class Ponto:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Drone:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.bsRaio = 5
        self.mapa = list()
        self.pernas = [[8, 2, 8], [3, 2, 5], [7, 2, 5]]
        self.zoom = 10
        self.port = 0
        self.id = randint(0, 255)

    # self.estado = 1gi

    def moveBy(self, x, y, z):
        self.dx = x
        self.dy = y
        self.dz = z

    def addPontos(self, pontos, zoom):
        # x = 0, z = 14
        #pontoAux = ponto[0][14]
        setores = [list() * 9]

        for x in range(15):
            for z in range(15, 0):
                if pontos[x][z] == 255:
                    pontos[x][z] = -1

                p = Ponto((x - 7) * zoom + self.dx, pontos[x][z], (z - 7) * zoom + self.dz)

                #define setor ao qual o ponto pertence
                a = 2
                b = 2

                if x < 5:
                    a = 0
                elif x < 10:
                    a = 1

                if z >= 10:
                    b = 0
                elif z >= 5:
                    b = 1

                setores[3 * b + a].append(p)

        return setores

    def chooseDirection(self, setores):
        v1 = 0
        v2 = 0
        i = 0
        choice = 0
        cMed = 0

        # calc por variancia
        for s in setores:
            soma = 0
            ptos = 0

            for h in s:
                if h >= 0:
                    soma += h
                    ptos += 1

            med = float(soma / ptos)
            var = float(pow(soma - med * ptos, 2) / ptos)

            if i == 0:
                v1 = var
                cMed = med
            elif var < v1:
                choice = i
                cMed = med

            i += 1

        x = 5 * self.zoom
        z = 5 * self.zoom

        if choice in [3, 4, 5]:
            z = 0
        elif choice in [6, 7, 8]:
            z = -z

        if choice in [0, 3, 6]:
            x = -x
        elif choice in [1, 4, 7]:
            x = 0

        self.zoom -= 1

        y = -(float((self.dy - cMed) / 10))

        if self.zoom == 1:
            y = - self.dy + cMed + 2

        self.moveBy(x, y, z)

        return self.sendPayload()

    def sendPayload(self):
        return ClientPayload(self)