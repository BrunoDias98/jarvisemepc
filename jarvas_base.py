import numpy as np
from osgeo import ogr
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import os, sys
import math

print(os.getcwd())

# Paths might need to be changed 
input = "5"
shapefile = ogr.Open(os.getcwd() + f"/Input/Pontos/Pontos{input}.shp")
if(shapefile == None):
    print("Erro ao abrir o shapefile") 

# In order to block prints, uncomment the following line
#sys.stdout = open(os.devnull, 'w')

layer = shapefile.GetLayer(0)

################################
####    Variaveis Globais  #####
################################
nrPoints = layer.GetFeatureCount()
setOfPoints = np.zeros((nrPoints+1,2))
distMaxEntrePontos = 60

def setOfPointsCreator():
    print("Total de pontos -> " , nrPoints)
    for i in range(nrPoints):
            feature = layer.GetFeature(i)
            geom = feature.GetGeometryRef()
            setOfPoints[i][0] = geom.GetX()
            setOfPoints[i][1] = geom.GetY()

def angulo(a,b,c):
    ang = math.degrees(
        math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    if ang < 0:
        ang = 360 + ang
    return ang

def distEntrePontosMilhasNauticas(p1,p2):
    return geodesic((p1[1],p1[0]),(p2[1],p2[0])).miles * 1.15078

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

        for i in range(nrPoints):
            if(distEntrePontosMilhasNauticas(setOfPoints[anchor],setOfPoints[i]) < distMaxEntrePontos):
                
                isThereAlready_intersects = 1

                angle = angulo(setOfPoints[start], setOfPoints[anchor], setOfPoints[i])
                # print(setOfPoints[i], angle)    


                if angle > maxAngle:


                    # Otimizar TODO
                    
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
                    
                    #MARTELADA GRAVEEEEEEEE
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
            
def plots(mi,a, h):
    for i in range(nrPoints):
        plt.plot(setOfPoints[i][0], setOfPoints[i][1], "ro") 
    for i in range(1,len(h)):
        plt.plot(setOfPoints[h[i]][0], setOfPoints[h[i]][1], "bo")
    plt.plot(setOfPoints[mi][0],setOfPoints[mi][1],"go")
    plt.plot(setOfPoints[a][0],setOfPoints[a][1],"gx")
    ax = plt.gca()
    ax.set_aspect('equal', adjustable='box')
    plt.savefig(f"../Output/sol_{input}.pdf")
    plt.show()

if __name__ == "__main__":

    setOfPointsCreator()
    # Lowest longitude  
    start = np.argmin(setOfPoints[:,0])
    # Lowest latitude and longitude -> Be careful because if there are values higher than 0, 
    # the value of the points assigned at   the beginning, since i use npzeros
    # Vai levar martelada...
    setOfPoints[nrPoints][0] = setOfPoints[start][0]
    setOfPoints[nrPoints][1] = 90 
    setOfPoints[nrPoints][1] = setOfPoints[np.argmin(setOfPoints[:,1])][1]

    hull = computeHull(nrPoints, start)

    for i in range(len(hull)):
        print(i, hull[i], setOfPoints[hull[i]])

    plots(start, nrPoints, hull)
    

