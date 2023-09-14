import numpy as np
import time
from geopy.distance import geodesic
from geovectorslib import direct, inverse

np.random.seed(42)

lats1 = np.random.uniform(-90,90,50)
lons1 = np.random.uniform(-180,180,50)
lats2 = np.random.uniform(-90,90,50)
lons2 = np.random.uniform(-180,180,50)
brgs = np.random.uniform(0,360,50)
dist = np.random.uniform(0,20e6,50)

start = time.time()
direct(lats1, lons1, brgs, dist)
print("vectorized: ", time.time() - start)

# geographiclib loop
start = time.time()
vectorized = [geodesic((lats1[i], lons1[i]), (lats2[i], lons2[i])).meters for i in range(len(lats1))]

start = time.time()
linear = inverse(np.full(50,lats1[0]), np.full(50,lons1[0]), lats2, lons2)
print("linear: ", time.time() - start)

print(vectorized)

print(linear["s12"])

