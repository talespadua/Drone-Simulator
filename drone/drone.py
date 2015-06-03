from random import randint
from payload import ClientPayload, PayloadProperties
from interpol import interpolate
import functions as f

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
        self.energy = 5000
        
        self.bsRaio = 5
        self.pernas = [[8, 2, 8], [3, 2, 5], [7, 2, 5]]

        #Para estratégia de obter vetor de vento
        self.zoom = 1

        self.port = 0
        self.drone_id = randint(0, 255)

        self.islanding = False
        self.northAligned = True

        self.rotation = 0
        self.frontalVector = 0

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
        #Atualiza tempo de voo
        self.flyingTime += 1

        #Caso não esteja alinhado com o norte do mapa, realinhar
        if self.northAligned == False:
            self.rotation = -self.rotation
            self.dx = 0
            self.dy = 0
            self.dz = 0
            self.northAligned == True

            self.atualizaCombustivel()

            return

        #Caso esteja alinhado com o norte do mapa...
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

        #Converter (dx, dy, dz) em (frontal, normal, rotation)
        self.frontalVector = f.convertXZIntoFrontalVector(self.dx, self.dz)
        self.rotation = f.convertXZIntoRotationAngle(self.dx, self.dz)

        if self.rotation != 0:
            self.northAligned = False

        self.atualizaCombustivel()

    def atualizaCombustivel(self):
        #Combustível
        self.energy -= f.convertXZIntoFrontalVector(self.dx, self.dz)

        #Gasta energia p/ subir
        if self.dy > 0:
            self.energy -= self.dy

        #Gasta energia se for para ficar parado
        elif self.dy == 0 and self.dx == 0 and self.dz == 0:
            self.energy -= 1

        #Conseiderando que deixar o drone em queda livre o faça cair 1dm/unidade de tempo
        elif self.dy < -1:
            self.energy += self.dy

        #Se o drone ficar sem combustivel
        if self.energy <= 0:
            print("Manhê!!! O droninho caiu!!!")

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

        #Limitando o deslocamento máximo por combustível restante
        #Estimando que 60% do combustível do drone será utilizado para movimento em XZ
        #Sem considerar conversão p/vetor frontal + rotação
        fuelLimit = int(round(self.energy * 0.6))

        if self.northLimit > fuelLimit:
            self.northLimit = fuelLimit
        if self.southLimit > fuelLimit:
            self.southLimit = fuelLimit
        if self.eastLimit > fuelLimit:
            self.eastLimit = fuelLimit
        if self.westLimit > fuelLimit:
            self.westLimit = fuelLimit

    def addPontos(self, pontos):
        print("addPontos")

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

        #Interpola pontos e adiciona no mapa, caso zoom > 1:
        if self.zoom > 1:
            self.interpolaPontos()

        #Remove pontos muito distantes (maxDist = +- 27)
        for p in self.mapa:
            deltaX = self.pontoCentral.x - p.x
            deltaZ = self.pontoCentral.z - p.z

            if deltaX < -27 or deltaX > 27 or deltaZ < -27 or deltaZ > 27:
                self.mapa.pop(self.mapa.index(p))

        #Ordena pontos do mapa do drone
        self.mapa.sort(key = lambda ponto: (ponto.x, ponto.z))

        self.setSafeLimits(pontos)

    def interpolaPontos(self):
        print("interpolaPontos")
        auxMap = list()

        prevPoint = self.mapa[0]

        for pa in self.mapa:
            deltaX = prevPoint.x - pa.x
            deltaZ = prevPoint.z - pa.z

            #Tentar reduzir a quantidade de interpolações!
            #Válido aumentar a distancia mínima entre os PAs de interpolação
            if (deltaX < 2 or deltaX > -2) and (deltaZ < 2 or deltaZ > -2):
                print("shouldnt:", deltaX, deltaZ)

            pb = Ponto(0, -1, 0)
            pc = Ponto(0, -1, 0)
            pd = Ponto(0, -1, 0)

            #Procura pelos outros pontos(b, c, d) p/ interpolar
            for proc in self.mapa:
                if proc.x == pa.x + self.zoom and proc.z == pa.z and pb.y == -1:
                    pb = proc
                if proc.x == pa.x and proc.z == pa.z + self.zoom and pc.y == -1:
                    pc = proc
                if proc.x == pa.x + self.zoom and proc.z == pa.z + self.zoom and pd.y == -1:
                    pd = proc

            #Encontrou os pontos necessários
            if pb.y > -1 and pc.y > -1 and pd.y > -1:
                interpList = interpolate(pa, pb, pc, pd)

                #Procura se esse ponto já existe no mapa
                for ponto in interpList:
                    matches = [fp for fp in self.mapa if fp.x == ponto.x and fp.z == ponto.z]
                    auxMatches = [fp for fp in auxMap if fp.x == ponto.x and fp.z == ponto.z]

                    #Verifica se esse ponto já foi mapeado antes
                    if len(matches) == 0 and len(auxMatches) == 0:
                        auxMap.append(Ponto(ponto.x, ponto.y, ponto.z))

        self.mapa.extend(auxMap)

    def chooseDirection(self, payload):
        print("chooseDirection")

        #Verifica se vai ou não comparar vento
        if self.flyingTime < 2:
            if self.energy > 0:
                self.moveBy(0, 0, 0)
            else:
                self.moveBy(0, -1, 0)

            if self.flyingTime >= 2:
                self.zoom = 5

            return self.sendPayload(payload)

        #Primeiro criar setores 11x11
        setores = list()

        firstPoint = self.mapa[0]
        lastPoint = self.mapa[-1]

        itX = firstPoint.x
        itZ = firstPoint.z

        while 1:
            matches = [fp for fp in self.mapa if itX <= fp.x < itX + 11 and itZ <= fp.z < itZ + 11]

            #Caso forme uma matriz 11x11
            if len(matches) == 121:
                setores.append(matches)

            itX += 5

            #Caso estoure o limite máximo do mapa em x
            if itX > lastPoint.x - 11:
                itX = firstPoint.x
                itZ += 5

            #Caso em z
            if itZ > lastPoint.z - 11:
                break

        print("pontos no mapa: ", len(self.mapa))
        print("setores: ", len(setores))

        #calc por variancia
        i = 0
        choice = -1
        cMed = 0
        cVar = 0

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

        #Encontra ponto central do setor
        pCentralSetor = setores[choice][60]
        x = pCentralSetor.x - self.pontoCentral.x
        z = pCentralSetor.z - self.pontoCentral.z


        #De acordo com o zoom, reduz altitude
        y = (- self.absY + cMed) / self.zoom

        self.moveBy(x, int(y), z)

        self.zoom -= 1
        if self.zoom == 0:
            self.zoom += 3 # zoom não pode ser 0, ele encerra erradamente, pousando no mesmo espaço.

        return self.sendPayload(payload)

    def testePouso(self, payload):
        # print("TestePouso")

        #Trens de pouso
        pa = Ponto(0, -1, 0)
        pb = Ponto(0, -1, 0)
        pc = Ponto(0, -1, 0)

        #Procura dentro de um range uma posição para pousar
        for x in range(-self.westLimit, self.eastLimit):
            for z in range(-self.southLimit, self.northLimit):
                #Procura pontos para cada trem de pouso
                for fp in self.mapa:
                    if fp.x == 3 + x + self.pontoCentral.x and self.z == 3 + z + self.pontoCentral.z:
                        pa = fp
                    elif fp.x == -2 + x + self.pontoCentral.x and self.z == 0 + z + self.pontoCentral.z:
                        pb = fp
                    elif fp.x == 2 + x + self.pontoCentral.x and self.z == 0 + z + self.pontoCentral.z:
                        pc = fp

                #Calcula desnível entre trens de pouso
                if pa.y > -1 and pb.y > -1 and pc.y > -1:
                    deltaAB = pa.y - pb.y
                    deltaAC = pa.y - pc.y
                    deltaBC = pb.y - pc.y

                    #Tolera um pouco de desnível
                    if -1 <= deltaAB <= 1 and -1 <= deltaAC <= 1 and -1 <= deltaBC <= 1:
                        self.moveBy(x, -self.absY + pb.y + 3, z)
                        self.islanding = True
                        return self.sendPayload(payload)

        #Caso não tenha dado pra pousar
        self.zoom += 1
        self.moveBy(randint(-self.westLimit, self.eastLimit), 10, randint(-self.southLimit, self.northLimit))
        return self.sendPayload(payload)

    def sendPayload(self, payload):
        #Passar muitos parâmetros, como das mensagens
        payload.add_zoom(self.zoom)

        #Por hora, usando frontal=z, binormal=y, normal=x
        payload.add_drone_normal_vector(self.dy)
        payload.add_drone_frontal_vector(self.frontalVector)
        payload.add_drone_rotation(self.rotation)

        if self.islanding:
            payload.add_msg_type(1)
            print("\n\nPouso executado com sucesso. Encerrando simulação...")

        else:
            payload.add_msg_type(0)

        return payload