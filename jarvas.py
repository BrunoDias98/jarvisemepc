import numpy as np
from osgeo import ogr
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import os, sys
import math
from scipy import spatial

############################################################################
################################
#   OVERLEAF TODO

# Quad trees
# Nearest Neighbor
# KDTree

#################################
############################################################################

# In order to block prints, uncomment the following line
#sys.stdout = open(os.devnull, 'w')

################################
####    Variaveis Globais  #####
################################

# Paths might need to be changed 
print(os.getcwd())
input = "2_5_project"
shapefile = ogr.Open(os.getcwd() + f"/../Input/shapes-finais/2_5_projectadas/edberg_{input}.shp")
if(shapefile == None):
    print("Erro ao abrir o shapefile") 
layer = shapefile.GetLayer(0)

nrPoints = layer.GetFeatureCount()
setOfPoints = np.zeros((nrPoints+1,2))
#TODO
#Esta distancia tem que ser milhas nauticas considerando a projecao e a euclidade
# TODO -> Projetar e reprojetar
distMaxEntrePontos = 60000

tree = None

#TODO
#Set of points creator -> kdtree creator
def setOfPointsCreator():
    print("Total de pontos -> " , nrPoints)
    for i in range(nrPoints):
            feature = layer.GetFeature(i)
            geom = feature.GetGeometryRef()
            setOfPoints[i][0] = geom.GetX()
            setOfPoints[i][1] = geom.GetY()
#TODO
#Angulos considerando a geodesia
def angulo(a,b,c):
    ang = math.degrees(
        math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    if ang < 0:
        ang = 360 + ang
    return ang

#TODO
#Confirmar que a formula está 100 por cento accurate
def distEntrePontosMilhasNauticas(p1,p2):
    return geodesic((p1[1],p1[0]),(p2[1],p2[0])).miles * 1.15078


#TODO
#Entender e explicar
def orientation(p, q, r):
    '''
    In order to find the orientation of an ordered triplet (p,q,r) function returns the following values:
    0 : Collinear points
    1 : Clockwise points
    2 : Counterclockwise
    See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/ for details of below formula. '''

    val = (setOfPoints[q][0] - setOfPoints[p][0]) * (setOfPoints[r][1] - setOfPoints[q][1]) - (setOfPoints[q][1] - setOfPoints[p][1]) * (setOfPoints[r][0] - setOfPoints[q][0])
    if (val > 0):
        # Clockwise orientation
        return 1
    elif (val < 0):
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0

#TODO
#Entender e explicar
# https://www.cdn.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
def do_intersect(p1, q1, p2, q2):
    '''Main function to check whether the closed line segments p1 - q1 and p2 
       - q2 intersect'''
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # General case
    if (o1 != o2 and o3 != o4):
        return True
    
    return False 

#TODO
#KDTREES
# def kdtreeCreator():
#     return "https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html"  
#   https://dl.acm.org/doi/10.1145/361002.361007 
# https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KDTree.html#sklearn.neighbors.KDTree


#TODO
#Criar funcoes auxiliares
#Medir os tempos
#De cada iteracao
#De cada bloco
#Medir complexidades
def computeHull(start, anchor): 

    result = []
    end = anchor
    result.append(anchor)

    # flag de debugger
    j = 0

    while True:

        print("\n Iteracao -> " ,j, " : A -> ", setOfPoints[start], " B (Ancora) ->", setOfPoints[anchor], "\n")

        maxAngle = 0
        chosenOne = None


        # milhasNauticasEmKm = 60 * oqueseja
        milhasNauticasEmKm = distMaxEntrePontos
        print("\nOI\n\n\n",tree)
        vizinhos = tree.query_ball_point(setOfPoints[anchor],milhasNauticasEmKm)

        for i in vizinhos:
            isThereAlready_intersects = 1
            angle = angulo(setOfPoints[start], setOfPoints[anchor], setOfPoints[i])
            print(setOfPoints[i], angle)       

            if angle > maxAngle:

                for iRes in range(len(result)-3, -1, -1):
                    if(do_intersect(anchor, i, result[iRes], result[iRes+1])):
                        isThereAlready_intersects = 0
                        break

                if(isThereAlready_intersects):
                    for iRes in result:
                        if(setOfPoints[iRes]==setOfPoints[i]).all():
                            isThereAlready_intersects = 0
                            print("##########################Aqui\n\n\n")
                            break
                
                if(isThereAlready_intersects or i == end):
                    maxAngle = angle
                    chosenOne = i

        if chosenOne != None:

            print("\nA -> ",setOfPoints[start], ": B -> " , setOfPoints[anchor], ": C ->", setOfPoints[chosenOne],"\n")

            start = anchor
            anchor = chosenOne
            result.append(anchor)

            j+=1
            
            print(result)

            if(anchor == end):
                break

        else:
            print("\n#########\nFailed\n#########\n")
            break

    return result

    #     for i in range(nrPoints):

    #         #TODO 
    #         #Substituir com a search na kdtree
    #         if(distEntrePontosMilhasNauticas(setOfPoints[anchor],setOfPoints[i]) < distMaxEntrePontos):
                
    #             #TODO 
    #             #Aclarar esta variavel
    #             isThereAlready_intersects = 1

    #             angle = angulo(setOfPoints[start], setOfPoints[anchor], setOfPoints[i])
    #             print(setOfPoints[i], angle)    

    #             if angle > maxAngle:

    #                 #TODO 
    #                 #Otimizar, so e preciso ir verificar se o ponto iRes estiver perto, quando estiver +60 ja nao
    #                 #Cuidado e com as concavidades, pq o res[70-50] pode estar, res[50-30] nao mas res[30-0] estar
    #                 #Senao tem que haver outra forma de verificar isto
    #                 #Talvez o ciclo acima chegue perfeitamente, evita-se o abaixo
    #                 for iRes in range(len(result)-3, -1, -1):
    #                     if(do_intersect(anchor, i, result[iRes], result[iRes+1])):
    #                         isThereAlready_intersects = 0
    #                         break
    #                 #TODO
    #                 #Comentarios acima
    #                 if(isThereAlready_intersects):
    #                     for iRes in result:
    #                         if(setOfPoints[iRes]==setOfPoints[i]).all():
    #                             isThereAlready_intersects = 0
    #                             print("##########################Aqui\n\n\n")
    #                             break
                    
    #                 #TODO 
    #                 #Tirar esta martelada
    #                 #Talvez retirar portugal continental da equacao, A ZEE
    #                 #de forma a obter ponto inicial e final
    #                 #MARTELADA GRAVEEEEEEEE
    #                 if(isThereAlready_intersects or i == end):
    #                     maxAngle = angle
    #                     chosenOne = i

    #     if chosenOne != None:

    #         print("\nA -> ",setOfPoints[start], ": B -> " , setOfPoints[anchor], ": C ->", setOfPoints[chosenOne],"\n")

    #         start = anchor
    #         anchor = chosenOne
    #         result.append(anchor)

    #         j+=1
            
    #         print(result)

    #         if(anchor == end):
    #             break

    #     else:
    #         print("\n#########\nFailed\n#########\n")
    #         break

    # return result

#TODO
#Plot dinamico
#Aumentar a pixelagem das imagens
def plots(mi,a, h):
    for i in range(nrPoints):
        plt.plot(setOfPoints[i][0], setOfPoints[i][1], "ro") 
    for i in range(1,len(h)):
        plt.plot(setOfPoints[h[i]][0], setOfPoints[h[i]][1], "bo")
    plt.plot(setOfPoints[mi][0],setOfPoints[mi][1],"go")
    plt.plot(setOfPoints[a][0],setOfPoints[a][1],"gx")
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    # plt.savefig(f"../Output/sol_{input}.pdf")
    plt.show()


# TODO
# Medir memoria - https://www.geeksforgeeks.org/monitoring-memory-usage-of-a-running-python-program/
if __name__ == "__main__":

    #TODO
    #Criar pontos de Hedberg a partis dos FOS
    #Dropar os pontos interiores
    #Juntar os pontos de Gardiner tambem
    #Colocar isto na kdtree

    setOfPointsCreator()

    tree = spatial.KDTree(setOfPoints)

    #TODO
    # Nao criar as 2 estruturas
    # tree = KDTree(setOfPoints)
    # print(tree.get_tree_stats())
    # Lowest longitude  
    start = np.argmin(setOfPoints[:,0])
    # Lowest latitude and longitude -> Be careful because if there are values higher than 0, 
    # the value of the points assigned at   the beginning, since i use npzeros
    # Vai levar martelada...
    setOfPoints[nrPoints][0] = setOfPoints[start][0]
    setOfPoints[nrPoints][1] = 90
    setOfPoints[nrPoints][1] = setOfPoints[np.argmin(setOfPoints[:,1])][1]

    hull = computeHull(nrPoints, start)

    #TODO
    #Clipar a solucao
    #Voltar a repetir a maximizacao
    #Lista de pontos 
    #Mapa visual

    #TODO 
    #Processar ZEE, Limite menos restritivo

    #TODO
    #Criar um menu/command line que pede argumentos
    #Tal como e a distancia entre pontos (0.5 milhas default)
    
    #TODO
    #Calculo da area

    # for i in range(len(hull)):
        # print(i, hull[i], setOfPoints[hull[i]])

    plots(start, nrPoints, hull)
    

