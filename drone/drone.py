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
        self.dy = 0
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

        print("Movimento nesta iteração: x:%d y:%d z:%d" %(x, y, z))

        #Calcula diferença entre o proximo ponto e o ponto inicial(0, 80, 0)
        self.pontoCentral.x += x
        self.pontoCentral.y += y
        self.pontoCentral.z += z

    def addPontos(self, pontos):
        setores = list()
        for i in range(5):
            setores.append(list())

        for x in range(15):
            for z in range(15):
                if pontos[x][z] == 255:
                    pontos[x][z] = -1

                p = Ponto((x - 7) * self.zoom + self.dx, pontos[x][z], (z - 7) * self.zoom + self.dz)

                #ignora pontos fora da memória do drone
                if p.y > -1:
                    #Adiciona ponto no mapa do drone
                    pMapa = Ponto(p.x + self.pontoCentral.x, p.y, p.z + self.pontoCentral.z)

                    if pMapa not in self.mapa:
                        self.mapa.append(pMapa)

                #Adiciona pontos aos setores
                if x < 10:
                    if z < 10:
                        setores[1].append(p)
                    if 5 <= z < 15:
                        setores[3].append(p)

                if 2 <= x < 13 and 2 <= z < 13:
                    setores[0].append(p)

                if 5 <= x < 15:
                    if z < 10:
                        setores[2].append(p)
                    if 5 <= z < 15:
                        setores[4].append(p)

        #Ordena pontos do mapa do drone
        self.mapa.sort(key = lambda ponto: (ponto.x, ponto.z))

        return setores

    def chooseDirection(self, setores):
        i = 0
        choice = -1
        cMed = 0
        cVar = 0

        firstValid = 0

        #calc por variancia
        for pts in setores:
            soma = 0
            nPtos = 0

            setorNeg = 0

            for h in pts:
                if h.y >= 0:
                    soma += h.y
                    nPtos += 1
                else:
                    setorNeg = 1
                    break

            # Verifica se no setor há algum ponto inválido
            if setorNeg == 0:
                firstValid = 1
                med = float(soma / nPtos)

                sVar = 0

                for h in pts:
                    sVar += pow(h.y - med, 2)

                var = float(sVar / nPtos - 1)


                if firstValid == 1:
                    cMed = med
                    cVar = var
                    choice = i
                elif var < cVar:
                    choice = i
                    cMed = med
                    cVar = var

            i += 1

        x = 2 * self.zoom
        z = 2 * self.zoom

        #Caso a média ou variância seja muito alta ou nenhum setor tenha sido escolhido
        #Vale alterar possíveis valores de cVar (no caso, aqui ele também é influenciado pelo zoom)
        if cMed > 200 or cVar > 50 * self.zoom or choice == -1:
            #Aumenta área de procura
            if self.zoom < 5:
                self.zoom += 1

            #Move um pouco p/pegar área diferente
            self.moveBy(randint(-5, 5), 0, randint(-5, 5))
            return self.sendPayload()

        #Escolhe setor
        if choice in [1, 3]:
            x = -x
        if choice in [3, 4]:
            z = -z

        elif choice == 0:
            x = 0
            z = 0


        #De acordo com o zoom, reduz altitude
        y = (- self.absY + cMed) / self.zoom

        self.moveBy(x, int(y), z)

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

        self.zoom += 1
        self.moveBy(randint(-5, 5), 10, randint(-5, 5))
        return self.sendPayload()

    def sendPayload(self):
        payload = ClientPayload()

        payload.add_port(self.port)
        payload.add_id(self.id)
        payload.add_zoom(self.zoom)

        #TODO: Implement vector approach
        #payload.add_params(params)
        #payload.add_drone_xpos(self.dx)
        #payload.add_drone_ypos(self.dy)
        #payload.add_drone_zpos(self.dz)
        #payload.add_drone_land_info(self.islanding)

        #Por hora, usando frontal=z, binormal=y, normal=x
        payload.add_drone_normal_vector(self.dx)
        payload.add_drone_frontal_vector(self.dz)
        payload.add_drone_binormal_vector(self.dy)

        if self.islanding:
            payload.add_msg_type(1)
            print("\n\nPouso executado com sucesso. Encerrando simulação...")

        else:
            payload.add_msg_type(0)

        return payload