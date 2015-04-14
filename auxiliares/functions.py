# Este método prepara uma matriz 15x15 dada a posição de um drone, e seu zoom. Ele devolve a matriz.
def getArrayToDrone(sentX, sentZ, zoom):
    baseX = sentX - 7*zoom;
    baseZ = sentZ - 7*zoom;

    gridSizeX = 50 #Este valor define o tamanho da matriz usada. Se um ponto exceder este valor na matriz original, devolve 255. Variavel global.
    gridSizeZ = 50

    returningArray[15][15]
    for i in range(0, 15):
    for j in range(0, 15):
        validSlot = 1 # Se isto setar em 0, acessou um ponto inexistente na matriz
            nextX = baseX + (zoom * i)
            if nextX < 0:
                validSlot = 0
            if nextX > gridSizeX:
                validSlot = 0
            nextZ = baseZ + (zoom * i)
            if nextZ < 0:
                validSlot = 0
            if nextZ > gridSizeZ:
                validSlot = 0


            if validSlot:
                returningArray[i][j] = mapa[baseX + (zoom * i)][baseZ + (zoom * j)] # Mapa deve ser global
            else:
                returningArray[i][j] = 255
   
    print "Matrix generated"
    return returningArray



# Este metodo verifica a colisão instanciando uma matriz temporária, traçando retas entre as bordas das areas dos circulos, e então rodando um grafo de busca à largura nele. Obs.: Pode demorar em casos grandes.
# Retorna -1 em caso de colisão.
# Retorna 1 em caso de sucesso.
def verifyCollision(previousX, previousZ, newX, newY, newZ):
    

	# O método constroi uma submatriz para tratamento posterior. Para isso, podemos diminuir o alcance corretamente
	if previousX > newX:
		newArrayXStart = newX - 5
		newArrayXEnd = previousX + 5
	else:
		newArrayXStart = previousX - 5
		newArrayXEnd = newX + 5

	if previousZ > newZ:
		newArrayZStart = newZ - 5
		newArrayZEnd = previousZ + 5
	else:
		newArrayZStart = previousZ - 5
		newArrayZEnd = newZ + 5

	# Se o X ou Z iniciais estiverem fora da própria grande matriz, o drona saiu do mapa. Colisão.
	if newArrayXStart < 0 or newArrayZStart < 0 or newArrayXEnd > gridSizeX or newArrayZEnd > gridSizeZ:
		print "Colisão"
		return -1

	newArray = [newArrayXEnd - newArrayXStart][newArrayZEnd - newArrayZStart]

	# Sets all to 0.
	for i in range(0, newArrayXEnd - newArrayXStart):
		for j in range(0, newArrayZEnd - newArrayZStart):
			newArray[i][j] = 0

	#Desenha reta entre quadrados Como as margens da submatriz são limitadas pelas pontas dos quadrados, temos apenas que traçar entre eles.
	lineAngle = 0 # 0 é diagonal direita cima -> baixo esquerda. Isto ocorre se um dos pontos for maior/menor em X e ao mesmo tempo em Z em relação ao outro

	if newX > previousX:
		if newZ < previousZ:
			lineAngle = 1 # X maior e Z menor -> inverte
	if newX > previousX:
		if newZ > previousZ:
			lineAngle = 1# X maior e Z menor -> inverte

	if lineAngle == 0:
		line(newArray, 0, gridSizeZ - 10, gridSizeX - 10, 0)
		line(newArray, 10, gridSizeZ, gridSizeX, 10)
	else:
		line(newArray, gridSizeX - 10, 0, 0, gridSizeZ - 10)
		line(newArray, gridSizeX, 10, 10, gridSizeZ)


	# Roda um grafo simples de espalhamento breadth-First pelo espaço definido. A cada iteração ele compara a altura y - 3 enviada (Ponto 2 da altura da nave) com o mapa. Se for menor ou igual, retorna colisão.
	for i in range(0, newArrayXEnd - newArrayXStart):
		for j in range(0, newArrayZEnd - newArrayZStart):

	graphQueue = Queue()
	graphQueue.enqueue(previousX)
	graphQueue.enqueue(previousZ)
	while (graphQueue.size() > 0):
		#Pega X e Z enfileirados
		graphX = graphQueue.dequeue()
		graphZ = graphQueue.dequeue()

		if mapa[i + newArrayXStart][j + newArrayZStart] < newY - 3: # note que ele soma os valores base de X e Z pré-geração do novo array. Isto da a posição correta no mapa.
					newArray[i][j] = 1
				else:
					print "Colisão"
					return -1

		#para cara verificação de adjacencia com valor 0, adiciona-se os X e Z novos para verificar. Obs.: JAMAIS MUDAR A ORDEM DE X E Z.
		if newArray[graphX + 1][graphZ] == 0:
			graphQueue.enqueue(graphX + 1)
			graphQueue.enqueue(graphZ)

		if newArray[graphX - 1][graphZ] == 0:
			graphQueue.enqueue(graphX - 1)
			graphQueue.enqueue(graphZ)

		if newArray[graphX][graphZ + 1] == 0:
			graphQueue.enqueue(graphX)
			graphQueue.enqueue(graphZ + 1)

		if newArray[graphX][graphZ - 1] == 0:
			graphQueue.enqueue(graphX)
			graphQueue.enqueue(graphZ - 1)
	print "Sem colisões neste movimento"

	return 1







# O metodo da linha de Bresenham define as bordas reais entre os pontos. Isto seta distancia enter pontos numa matriz em 1, mesmo que a linha projetada possua um angulo incomum.
def line(array, x0, y0, x1, y1):
	"Bresenham's line algorithm"
	dx = abs(x1 - x0)
	dy = abs(y1 - y0)
	x, y = x0, y0
	sx = -1 if x0 > x1 else 1
	sy = -1 if y0 > y1 else 1
	if dx > dy:
		err = dx / 2.0
		while x != x1:
			array[x][y] = 1
			err -= dy
			if err < 0:
				y += sy
				err += dx
			x += sx
	else:
		err = dy / 2.0
		while y != y1:
			self.set(x, y)
			err -= dx
			if err < 0:
				x += sx
				err += dy
			y += sy        
	array[x][y] = 1


