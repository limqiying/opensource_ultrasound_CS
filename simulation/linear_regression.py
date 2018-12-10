import csv, math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Plane:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Line:
    def __init__(self,x,y,z,e):
        self.x = x
        self.y = y
        self.z = z
        self.e = e

time_stamp = []
distance = []
with open('obs.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count != 0:
            time_stamp.append(row[0])
            distance.append(row[1])
        line_count+=1
time_stamp.reverse()
distance.reverse()

angle = 36*math.pi/180
points = []
start_point = 5
v = np.array([0, math.cos(25*math.pi/180), math.sin(25*math.pi/180)])
A = np.array([[math.cos(angle), 0, math.sin(angle)],[0,1,0],[-math.sin(angle), 0, math.cos(angle)]])
probe_coord = []

while start_point > -5:
    probe_coord.append([0, -1, start_point])

    div = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    unit_v = [v[0]/div, v[1]/div, v[2]/div]

    start_point -= 0.5
    dis = distance.pop()
    x = probe_coord[-1][0] + (unit_v[0]*float(dis))
    y = probe_coord[-1][1] + (unit_v[1]*float(dis))
    z = probe_coord[-1][2] + (unit_v[2]*float(dis))

    points.append([x,y,z])

    print("[{}, {}, {}]".format(x,y,z))
    v = A.dot(np.array(v))

# Plane Fitting
A = np.matrix([[i[0], i[1], 1] for i in points])
B = np.matrix([[i[2]] for i in points])
param = (A.T * A).I * A.T * B

# Plot Plane
xs = []
ys = []
zs = []
for i in points:
    xs.append(i[0])
    ys.append(i[1])
    zs.append(i[2])

# plot raw data
plt.figure()
ax = plt.subplot(111, projection='3d')
ax.scatter(xs, ys, zs, color='b')

# plot plane
xlim = ax.get_xlim()
ylim = ax.get_ylim()
X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]),
                  np.arange(ylim[0], ylim[1]))
Z = np.zeros(X.shape)
for r in range(X.shape[0]):
    for c in range(X.shape[1]):
        Z[r,c] = param[0] * X[r,c] + param[1] * Y[r,c] + param[2]
ax.plot_wireframe(X,Y,Z, color='k')

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()

