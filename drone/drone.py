from random import randint
from payload import ClientPayload, PayloadProperties

class Ponto:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Drone:
    def __init__(self):
        self.dx = 0
        self.dy = 80
        self.dz = 0

        self.bsRaio = 5
        self.pernas = [[8, 2, 8], [3, 2, 5], [7, 2, 5]]
        self.zoom = 5

        self.port = 0
        self.id = randint(0, 255)

        self.islanding = False
        # self.estado = 1

        # self.mapa = list()
        # self.pontoInicial = Ponto(0, 80, 0)
        # self.mapa[0].append(list())
        # self.mapa[0][0].append(self.pontoInicial)
        # self.pontoCentral = self.pontoInicial

    def moveBy(self, x, y, z):
        self.dx = x
        self.dy = y
        self.dz = z

        print("%d %d %d" %(x, y, z))

        #Calcula diferença entre o proximo ponto e o ponto inicial
        # self.pontoCentral.x += x
        # self.pontoCentral.y += y
        # self.pontoCentral.z += z

    def addPontos(self, pontos):
        setores = list()
        for i in range(9):
            setores.append(list())

        for x in range(15):
            for z in range(15):
                if pontos[x][z] == 255:
                    pontos[x][z] = -1

                p = Ponto((x - 7) * self.zoom + self.dx, pontos[x][z], (z - 7) * self.zoom + self.dz)

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
        i = 0
        choice = 0
        cMed = 0
        cVar = 0

        # calc por variancia
        for s in setores:
            soma = 0
            ptos = 0

            setorNeg = 0

            for h in s:
                if h.y >= 0:
                    soma += h.y
                    ptos += 1
                else:
                    setorNeg = 1
                    break

            if setorNeg == 0:
                med = float(soma / ptos)

                sVar = 0

                for h in s:
                    sVar += pow(h.y - med, 2)

                var = float(sVar / ptos - 1)


                if i == 0:
                    cMed = med
                    cVar = var
                elif var < cVar:
                    choice = i
                    cMed = med
                    cVar = var

                i += 1

        x = 5 * self.zoom
        z = 5 * self.zoom

        print("%.2f %.2f" %(cMed, cVar))

        #Caso a média seja muito alta
        if cMed > 200 or cVar > 2:
            self.moveBy(randint(-5, 5), 10, randint(-5, 5))
            return self.sendPayload()

        print("Setor: %d" %(choice))

        #Escolhe setor
        if choice in [3, 4, 5]:
            z = 0
        elif choice in [6, 7, 8]:
            z = -z

        if choice in [0, 3, 6]:
            x = -x
        elif choice in [1, 4, 7]:
            x = 0

        self.zoom -= 1
        if self.zoom == 0:
            self.zoom += 3 # zoom não pode ser 0, ele encerra erradamente, pousando no mesmo espaço.

        y = -((self.dy - cMed) / 10)

        self.moveBy(x, y, z)

        return self.sendPayload()

    def testePouso(self, pontos):
        print("TestePouso")
        for x in range(-2, 3):
            for z in range(-2, 3):
                y1 = pontos[9 + x][7 + z]
                y2 = pontos[5 + x][7 + z]
                y3 = pontos[10 + x][10 + z]

                if y1 == y2 and y2 == y3:
                    self.moveBy(0, -self.dy + y1 + 2, 0)
                    self.islanding = True
                    return self.sendPayload()

        self.zoom -= 1
        self.moveBy(randint(-5, 5), 10, randint(-5, 5))
        return self.sendPayload()

    def sendPayload(self):
        params = PayloadProperties()
        params.port = self.port
        params.id = self.id
        params.zoom = self.zoom
        payload = ClientPayload()
        payload.add_params(params)
        payload.add_drone_xpos(self.dx)
        payload.add_drone_ypos(self.dy)
        payload.add_drone_zpos(self.dz)
        payload.add_drone_land_info(self.islanding)
        if self.islanding:
            print("\n\nPouso executado com sucesso. Encerrando simulação...")
        return payload