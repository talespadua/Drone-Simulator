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
        self.absY = 80

        self.bsRaio = 5
        self.pernas = [[8, 2, 8], [3, 2, 5], [7, 2, 5]]
        self.zoom = 5

        self.port = 0
        self.id = randint(0, 255)

        self.islanding = False

        self.mapa = list()
        self.pontoInicial = Ponto(self.dx, self.dy, self.dz)
        self.pontoCentral = self.pontoInicial

    def moveBy(self, x, y, z):
        self.dx = x
        self.dy = y
        self.dz = z

        self.absY += y

        print("%d %d %d" %(x, y, z))

        #Calcula diferença entre o proximo ponto e o ponto inicial(0, 80, 0)
        self.pontoCentral.x += x
        self.pontoCentral.y += y
        self.pontoCentral.z += z

    def addPontos(self, pontos):
        setores = list()
        for i in range(9):
            setores.append(list())

        for x in range(15):
            for z in range(15):
                if pontos[x][z] == 255:
                    pontos[x][z] = -1

                p = Ponto((x - 7) * self.zoom + self.dx, pontos[x][z], (z - 7) * self.zoom + self.dz)

                #ignora pontos fora do mapa
                if p.y > -1:
                    #Adiciona ponto no mapa do drone
                    pMapa = Ponto(p.x + self.pontoCentral.x, p.y, p.z + self.pontoCentral.z)

                    if pMapa not in self.mapa:
                        self.mapa.append(pMapa)

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

        #Ordena pontos do mapa do drone
        self.mapa.sort(key = lambda ponto: (ponto.x, ponto.z))

        return setores

    def chooseDirection(self, setores):
        i = 0
        choice = -1
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
                    print("nope %d" % (i))
                    setorNeg = 1
                    break

            # Verifica se no setor há algum ponto inválido
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

        x = self.zoom
        z = self.zoom

        #Caso a média ou variância seja muito alta ou nenhum setor tenha sido escolhido
        if cMed > 200 or cVar > 2 or choice == -1:
            if self.zoom < 10:
                self.zoom += 1

            self.moveBy(randint(-1, 1), 10, randint(-1, 1))
            return self.sendPayload()

        #Escolhe setor
        if choice in [3, 4, 5]:
            z = 0
        elif choice in [6, 7, 8]:
            z = -z

        if choice in [0, 3, 6]:
            x = -x
        elif choice in [1, 4, 7]:
            x = 0

        y = (- self.absY + cMed) / self.zoom

        self.moveBy(x, y, z)

        self.zoom -= 1
        if self.zoom == 0:
            self.zoom += 3 # zoom não pode ser 0, ele encerra erradamente, pousando no mesmo espaço.

        return self.sendPayload()

    def testePouso(self, pontos):
        print("TestePouso")
        for x in range(-2, 3):
            for z in range(-2, 3):
                y1 = pontos[9 + x][7 + z]
                y2 = pontos[5 + x][7 + z]
                y3 = pontos[10 + x][10 + z]

                if y1 == y2 and y2 == y3:
                    self.moveBy(0, -self.absY + y1 + 3, 0)
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