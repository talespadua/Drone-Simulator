from random import randint
from payload import ClientPayload, PayloadProperties
from interpol import interpolate

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

        #Para estratégia de obter vetor de vento
        self.zoom = 1

        self.port = 0
        self.drone_id = randint(0, 255)

        self.islanding = False

        #Limites seguros de locomoção
        self.northLimit = 2 * self.zoom
        self.southLimit = 2 * self.zoom
        self.eastLimit = 2 * self.zoom
        self.westLimit = 2 * self.zoom

        #Mapa interno
        self.mapa = list()
        self.pontoInicial = Ponto(self.dx, self.dy, self.dz)
        self.pontoCentral = self.pontoInicial

        #Indicadores de vento
        self.normalWind = 0
        self.binormalWind = 0
        self.frontalWind = 0

        #Indicador de tempo de voo
        self.flyingTime = 0

    def moveBy(self, x, y, z):
        self.dx = x
        self.dy = y
        self.dz = z

        self.absY += y

        print("Movimento nesta iteração: x:%d y:%d z:%d" %(x, y, z))

        #Calcula diferença entre o ponto central do drone e o ponto inicial(0, 80, 0)
        self.pontoCentral.x += x
        self.pontoCentral.y += y
        self.pontoCentral.z += z

        #Atualiza limites seguros
        self.northLimit -= self.dz
        self.southLimit += self.dz
        self.eastLimit -= self.dx
        self.westLimit += self.dx

        #Atualiza tempo de voo
        self.flyingTime += 1

    def setSafeLimits(self, pontos):
        if not -1 < pontos[7][0] < self.absY - 5:
            self.northLimit = self.zoom
        else:
            self.northLimit = 0

        if not -1 < pontos[7][14] < self.absY - 5:
            self.southLimit = self.zoom
        else:
            self.southLimit = 0

        if not -1 < pontos[0][7] < self.absY - 5:
            self.westLimit = self.zoom
        else:
            self.westLimit = 0

        if not -1 < pontos[14][7] < self.absY - 5:
            self.eastLimit = self.zoom
        else:
            self.eastLimit = 0

    def addPontos(self, pontos):
        setores = list()
        for i in range(5):
            setores.append(list())

        for x in range(15):
            for z in range(15):
                #Valor que muito provavelmente é um erro de comunicação
                if pontos[x][z] > 250:
                    pontos[x][z] = -1

                p = Ponto((x - 7) * self.zoom + self.pontoCentral.x, pontos[x][z], (z - 7) * self.zoom + self.pontoCentral.z)

                #ignora pontos fora da memória do drone
                if p.y > -1:
                    #Busca se esse ponto já foi adicionado antes
                    matches = [fp for fp in self.mapa if p.x == fp.x and p.z == fp.z]

                    if len(matches) == 0:
                        self.mapa.append(p)
                    #Seja erro ou não, isso irá substituir alguma imprecisão da interpolação
                    else:
                        self.mapa.remove(matches[0])
                        self.mapa.append(p)

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

        #Interpola pontos e adiciona no mapa:
        self.interpolaPontos()

        #Ordena pontos do mapa do drone
        self.mapa.sort(key = lambda ponto: (ponto.x, ponto.z))

        self.setSafeLimits(pontos)

        return setores

    def interpolaPontos(self):
        interpList = list()
        auxMap = list()

        for pa in self.mapa:
            pb = Ponto(0, -1, 0)
            pc = Ponto(0, -1, 0)
            pd = Ponto(0, -1, 0)

            #Procura pelos outros pontos p/ interpolar
            for proc in self.mapa:
                if pa.x + self.zoom == proc.x and pa.z == proc.z:
                    pb = proc
                elif pa.x == proc.x and pa.z + self.zoom == proc.z:
                    pc = proc
                elif pa.x + self.zoom == proc.x and pa.z + self.zoom == proc.z:
                    pd = proc

            #Encontrou os pontos necessários
            if pb.y > -1 and pc.y > -1 and pd.y > -1:
                interpList = interpolate(pa, pb, pc, pd)

                for ponto in interpList:
                    matches = [fp for fp in self.mapa if fp.x == ponto.x and fp.z == ponto.z]
                    auxMatches = [afp for afp in auxMap if afp.x == ponto.x and afp.z == ponto.z]

                    #Verifica se esse ponto já foi mapeado antes
                    if len(matches) == 0 and len(auxMap) == 0:
                        print("append")
                        auxMap.append(ponto)

        self.mapa.extend(auxMap)
        print("d")

    def chooseDirection(self, setores, payload):
        if self.flyingTime < 2:
            self.moveBy(0, 0, 0)

            if self.flyingTime >= 2:
                self.zoom = 5

            return self.sendPayload(payload)

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
            print("NOPE")
            #Aumenta área de procura
            if self.zoom < 5:
                self.zoom += 1

            #Move um pouco p/pegar área diferente
            self.moveBy(randint(-self.westLimit, self.eastLimit), 0, randint(-self.southLimit, self.northLimit))
            return self.sendPayload(payload)

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

        return self.sendPayload(payload)

    def testePouso(self, pontos, payload):
        print("TestePouso")
        for x in range(-2, 3):
            for z in range(-2, 3):
                y1 = pontos[9 + x][7 + z]
                y2 = pontos[5 + x][7 + z]
                y3 = pontos[10 + x][10 + z]

                if y1 == y2 and y2 == y3:
                    self.moveBy(0, -self.absY + y1 + 3, 0)
                    self.islanding = True
                    return self.sendPayload(payload)

        self.zoom += 1
        self.moveBy(randint(-self.westLimit, self.eastLimit), 10, randint(-self.southLimit, self.northLimit))
        return self.sendPayload(payload)

    def sendPayload(self, payload):

        #TODO: acho melhor colocar os parametros do payload no metodo do client, acho mais consistente e não precisamos
        #Passar muitos parâmetros, como das mensagens
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