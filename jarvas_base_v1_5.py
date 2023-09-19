import numpy as np
from tqdm.auto import tqdm
from osgeo import ogr
import matplotlib.pyplot as plt
from geovectorslib import inverse
from geographiclib.geodesic import Geodesic
import os, sys
import math

print(os.getcwd())

# Paths might need to be changed 
input = "5"
# shapefile = ogr.Open(os.getcwd() + f"/jarvisemepc-main/Pontos/Pontos{input}_gardiner.shp")
shapefile = ogr.Open(os.getcwd() + f"/../Input/Pontos/Pontos{input}.shp")
# shapefile = ogr.Open(os.getcwd() + f"/jarvisemepc-main/Pontos/edberg_10/edberg_10.shp")
if(shapefile == None):
    print("Erro ao abrir o shapefile") 
    

# In order to block prints, uncomment the following line
#sys.stdout = open(os.devnull, 'w')

layer = shapefile.GetLayer(0)

################################
####    Variaveis Globais  #####
################################
nrPoints = layer.GetFeatureCount()
setOfPoints = np.zeros((nrPoints,2))
# setOfPoints = np.zeros((nrPoints+1,2))
# 60 nautical miles * meters per nautical mile
distMaxEntrePontos = 60*1852 

def setOfPointsCreator():
    print("Total de pontos -> " , nrPoints)
    for i in range(nrPoints):
            feature = layer.GetFeature(i)
            geom = feature.GetGeometryRef()
            setOfPoints[i][0] = geom.GetX()
            setOfPoints[i][1] = geom.GetY()

# iStart = 15403
# iEnd =  107277


def angulo(a,b,c):
    return np.degrees(np.arctan2(c[:,1]-b[1], c[:,0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])) % 360

def distEntrePontosMilhasNauticasEAngulo(p1,p2):
    return inverse(np.full(len(p2),p1[1]),np.full(len(p2),p1[0]),p2[:,1],p2[:,0])

def orientation(p, q, r):
    '''
    to find the orientation of an ordered triplet (p,q,r)
    function returns the following values:
    0 : Collinear points
    1 : Clockwise points
    2 : Counterclockwise
    See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/ 
    for details of below formula. 
    '''
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

    # # Special Cases - Sera que nao sao precisos?
    # # p1, q1 and p2 are colinear and p2 lies on segment p1q1
    # if (o1 == 0 and on_segment(p1, p2, q1)):
    #     return True

    # # p1, q1 and p2 are colinear and q2 lies on segment p1q1
    # if (o2 == 0 and on_segment(p1, q2, q1)):
    #     return True

    # # p2, q2 and p1 are colinear and p1 lies on segment p2q2
    # if (o3 == 0 and on_segment(p2, p1, q2)):
    #     return True

    # # p2, q2 and q1 are colinear and q1 lies on segment p2q2
    # if (o4 == 0 and on_segment(p2, q1, q2)):
    #     return True

    return False # Doesn't fall in any of the above cases

def computeHull(start, anchor, end=None):
    if end is None:
        # assumes roundtrip
        end = anchor

    result = []
    result.append(anchor)

    # flag de debugger
    j = 0
    with tqdm() as pbar:
        while True:
            pbar.set_description(desc=f"Iteracao -> {j} : A -> {setOfPoints[start]} B (Ancora) -> {setOfPoints[anchor]}")
            # pbar.update()
            # print("\n Iteracao -> " ,j, " : A -> ", setOfPoints[start], " B (Ancora) ->", setOfPoints[anchor], "\n")

            chosenOne = None

            # get the statistics, first key is the distances second is the angles
            geoStatistics = distEntrePontosMilhasNauticasEAngulo(setOfPoints[anchor],setOfPoints)
            inDistanceMask = geoStatistics["s12"] < distMaxEntrePontos

            notInResultMask = np.full(inDistanceMask.shape, True)
            notInResultMask[np.array(result)] = False
            notInResultMask[end] = True # edge-case for roundtrip (end == start)

            validPointsMask = inDistanceMask & notInResultMask
            validPoints = setOfPoints[validPointsMask]

            angles = angulo(setOfPoints[start], setOfPoints[anchor], validPoints)

            indexes = np.arange(nrPoints+1,dtype=int)[validPointsMask]

            sortedIndexes = np.argsort(angles)[::-1]

            angles = angles[sortedIndexes]
            indexes = indexes[sortedIndexes]
            for i in indexes:
                isThereAlready_intersects = 1
                for iRes in range(len(result) - 3, 0, -1):
                    if(do_intersect(anchor, i, result[iRes], result[iRes+1])):
                        isThereAlready_intersects = 0
                        break

                #MARTELADA GRAVEEEEEEEE
                if(isThereAlready_intersects):
                    chosenOne = i
                    break

            if chosenOne != None:

                # print("\nA -> ",setOfPoints[start], ": B -> " , setOfPoints[anchor], ": C ->", setOfPoints[chosenOne],"\n")

                start = anchor
                anchor = chosenOne
                result.append(anchor)

                j+=1
                
                # print(result)

                if(anchor == end):
                    break

            else:
                print("\n#########\nFailed\n#########\n")
                break

    return result

def computeArea(limit):
    geod = Geodesic.WGS84
    p = geod.Polygon()
    for point in limit:
        p.AddPoint(setOfPoints[point][0], setOfPoints[point][1])
    num, perim, area = p.Compute()
    return area

def plots(a, mi, h):
    plt.plot(setOfPoints[:, 0], setOfPoints[:, 1], "ro") 
    plt.plot(setOfPoints[h, 0], setOfPoints[h, 1], "bo-")
    # plt.plot(setOfPoints[ch, 0], setOfPoints[ch, 1], "go-")
    plt.plot(setOfPoints[mi][0],setOfPoints[mi][1],"go")
    plt.plot(setOfPoints[a][0],setOfPoints[a][1],"gx")
    # ax = plt.gca()
    # ax.set_aspect('equal', adjustable='box')
    # plt.savefig(f"../Output/sol_{input}.pdf")
    plt.show()


if __name__ == "__main__":

    #TODO 
    #O angulo azimuth
    #calculo da area ao centroide
    #inicio, fim, baixo, esquerda, cima, 5 vertices 4 arestas

    # start = setOfPoints[iStart]
    # end = setOfPoints[iEnd]

    print("\n\n\n Starting \n\n\n\n")
    setOfPointsCreator()
    old_nrPoints = nrPoints
    setOfPoints = np.unique(setOfPoints, axis=0) # drop duplicates
    nrPoints = len(setOfPoints) - 1 
    print(f"Dropped {(old_nrPoints - nrPoints)/old_nrPoints:.2%} ({old_nrPoints - nrPoints}/{old_nrPoints})")
    
    # iStart = np.where(setOfPoints == start)[0][0]
    # print(type(iStart))
    # iEnd = np.where(setOfPoints == end)[0][0]
    # # Checkpoints / Pool 
    # # Lowest longitude  
    # start = np.argmin(setOfPoints[:,0])
    # # Lowest latitude and longitude -> Be careful because if there are values higher than 0, 
    # # the value of the points assigned at   the beginning, since i use npzeros
    # # Vai levar martelada...
    # setOfPoints[nrPoints][0] = setOfPoints[start][0]
    # setOfPoints[nrPoints][1] = 90 
    # setOfPoints[nrPoints][1] = setOfPoints[np.argmin(setOfPoints[:,1])][1]


    print("\n\n\n Starting \n\n\n\n")
    # Primeiro -> 107277 (é um ponto gardiner) 
    # Último é o  15403  (é um ponto edberg  )
    

    # min long, max lat, min lat
    # plt.plot(setOfPoints[checkPoints[0][0]][0], setOfPoints[checkPoints[0][0]][1], "bo") 
    # plt.plot(checkPoints[0][1][0], checkPoints[0][1][1], "gx")
    # plt.plot(setOfPoints[checkPoints[1][0]][0], setOfPoints[checkPoints[1][0]][1], "bo") 
    # plt.plot(checkPoints[1][1][0], checkPoints[1][1][1], "gx")
    # plt.plot(setOfPoints[checkPoints[2][0]][0], setOfPoints[checkPoints[2][0]][1], "bo")
    # plt.plot(checkPoints[2][1][0], checkPoints[2][1][1], "gx")
    # # ax.set_aspect('equal', adjustable='box')
    # # plt.savefig(f"../Output/sol_{input}.pdf")
    # plt.show()


    iStarts = np.array([np.argmin(setOfPoints[:,1]),np.argmin(setOfPoints[:,0]),np.argmax(setOfPoints[:,1])])
    
    
    plt.plot(setOfPoints[:, 0], setOfPoints[:, 1], "ro")
    plt.plot(setOfPoints[iStarts,0], setOfPoints[iStarts,1], "bo") 
    plt.show()

    hull = []

    for iAnchor, iStart, iEnd, in zip(np.roll(iStarts,-1),iStarts,np.roll(iStarts,1)):
        hull += computeHull(iStart, iAnchor, end=iEnd)[:-1]
        plots(iStart, iAnchor, hull)




    # HERE
    # hull = computeHull(nrPoints, start)
    # hull = computeHull(nrPoints, start, iEnd)
    for i in range(len(hull)):
        print(i, hull[i], setOfPoints[hull[i]])
    
    area = computeArea(hull)
    print("Area: {:.5f} m^2".format(area))
    # plots([checkpoint[0] for checkpoint in checkPoints], hull)
    plots(iStart, iAnchor, hull)
    

