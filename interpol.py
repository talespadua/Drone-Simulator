class Ponto:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

#Considerando:
#     z
#     |
#     V
#x--->pa-----pb
#     |___|___|
#     |   |   |
#     pc-----pd

#Interpolação bilinear
def interpolate(pa, pb, pc, pd):
    #Interpolações lineares em x
    fab = list()
    fcd = list()
    fxz = list()

    xDist = pb.x - pa.x
    zDist = pc.z - pa.z

    #x^n tal que n = index na list
    fab.append(pb.x / xDist * pa.y - pa.x / xDist * pb.y)
    fab.append(-pa.y / xDist + pb.y / xDist)

    fcd.append(pd.x / xDist * pc.y - pc.x / xDist * pd.y)
    fcd.append(-pc.y / xDist + pd.y / xDist)

    #Interpolar em z
    #index = 0 = c, 1 = x, 2 = z, 3 = xz
    fxz.append(pc.z / zDist * fab[0] - pa.z / zDist * fcd[0])
    fxz.append(pc.z / zDist * fab[1] - pa.z / zDist * fcd[1])
    fxz.append(-fab[0] / zDist + fcd[0] / zDist)
    fxz.append(-fab[1] / zDist + fcd[1] / zDist)

    #Retornar respostas:
    resposta = list()

    for x in range(pa.x, pb.x + 1):
        for z in range(pa.z, pc.z + 1):
            y = fxz[0] + x * fxz[1] + z * fxz[2] + x * z *fxz[3]

            p = Ponto(x, round(y), z)
            resposta.append(p)

    return resposta