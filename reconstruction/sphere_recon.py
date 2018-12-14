import csv, math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as m3d
from scipy.optimize import leastsq


"""
Helper Functions
"""

count = 0

def plot():
    xs = []
    ys = []
    zs = []
    for i in points:
        xs.append(i[0])
        ys.append(i[1])
        zs.append(i[2])

    xp = []
    yp = []
    zp = []
    for i in proj_points:
        xp.append(i[0])
        yp.append(i[1])
        zp.append(i[2])

    # plot raw data
    fig = plt.figure()
    fig.suptitle('Iteration ' + str(count), fontsize=16)
    ax = fig.gca(projection='3d')
    ax.scatter(xs, ys, zs, color='b')
    ax.scatter(xp, yp, zp, color='r')
#     ax.scatter(xs[1], ys[1], zs[1], color='r')
#     ax.scatter(xp[1], yp[1], zp[1], color='r')

    # plot sphere
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = r*np.cos(u)*np.sin(v) + a
    y = r*np.sin(u)*np.sin(v) + b
    z = r*np.cos(v) + c
    ax.plot_wireframe(x, y, z, color="r")
    
    # Line fitting
    data = np.array(probe_coord)

    # Calculate the mean of the points, i.e. the 'center' of the cloud
    datamean = data.mean(axis=0)

    # Do an SVD on the mean-centered data.
    uu, dd, vv = np.linalg.svd(data - datamean)

    # Now vv[0] contains the first principal component, i.e. the direction
    # vector of the 'best fit' line in the least squares sense.
    # Now generate some points along this best fit line, for plotting.
    
    # I use -7, 7 since the spread of the data is roughly 14
    # and we want it to have mean 0 (like the points we did
    # the svd on). Also, it's a straight line, so we only need 2 points.
    linepts = vv[0] * np.mgrid[-7:7:2j][:, np.newaxis]
    
    # shift by the mean to get the line in the right place
    linepts += datamean
    
    ax.scatter3D(*data.T)
#     ax.scatter(probe_coord[1][0], probe_coord[1][1], probe_coord[1][2], color='r')
    ax.plot3D(*linepts.T)

    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.set_aspect(1)
    plt.show()
    
    
def resSphere(p,x,y,z):
    """ residuals from sphere fit """

    a,b,c,r = p                             # a,b,c are center x,y,z coords to be fit, r is the radius to be fit
    distance = np.sqrt( (x-a)**2 + (y-b)**2 + (z-c)**2 )
    err = distance - r                 # err is distance from input point to current fitted surface

    return err


"""
Reconstruction Process
"""

time_stamp = []
distance_1 = []
distance_2 = []
with open('obs_cube.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count != 0:
            time_stamp.append(row[0])
            distance_1.append(row[1])
            distance_2.append(row[2])
        line_count+=1

probe_coord = []
start_point = 5
while start_point > -5:
    probe_coord.append([0, -1, start_point])
    start_point -= 0.5

for itr in range(10):
    angle = 36*math.pi/180
    v = np.array([0, math.cos(25*math.pi/180), math.sin(25*math.pi/180)])
    R = np.array([[math.cos(angle), 0, math.sin(angle)],[0,1,0],[-math.sin(angle), 0, math.cos(angle)]])
    points = []
    for i in range(0,20):
        x1 = probe_coord[i][0] + (v[0]*float(distance_1[i]))
        y1 = probe_coord[i][1] + (v[1]*float(distance_1[i]))
        z1 = probe_coord[i][2] + (v[2]*float(distance_1[i]))
        points.append([x1,y1,z1])
        x2 = probe_coord[i][0] + (v[0]*float(distance_2[i]))
        y2 = probe_coord[i][1] + (v[1]*float(distance_2[i]))
        z2 = probe_coord[i][2] + (v[2]*float(distance_2[i]))
        points.append([x2,y2,z2])
        v = R.dot(np.array(v))

    # Sphere Fitting
    myX = np.array([i[0] for i in points])
    myY = np.array([i[1] for i in points])
    myZ = np.array([i[2] for i in points])
    init = [0.,0.,0.,0.]
    param = leastsq(resSphere, init, args=(myX,myY,myZ))[0]
    print(param)
    
    # 3D Projection onto the Sphere
    a = float(param[0])
    b = float(param[1])
    c = float(param[2])
    r = float(param[3])
    proj_points = []
    for point in points:
        norm = np.sqrt((point[0] - a)*(point[0] - a) + (point[1] - b)*(point[1] - b) + (point[2] - c)*(point[2] - c))
        proj_points.append([r * (point[0] - a)/norm, r * (point[1] - b)/norm, r * (point[2] - c)/norm])
    
    plot()
    count += 1
    
    # move the probe positions
    for i in range(0, 20):
        x_new = probe_coord[i][0] + (proj_points[i][0] - points[i][0])
        y_new = probe_coord[i][1] + (proj_points[i][1] - points[i][1])
        z_new = probe_coord[i][2] + (proj_points[i][2] - points[i][2])
        probe_coord[i] = [x_new, y_new, z_new]
    
    # Line fitting
    data = np.array(probe_coord)
    # Calculate the mean of the points, i.e. the 'center' of the cloud
    datamean = data.mean(axis=0)
    # Do an SVD on the mean-centered data.
    uu, dd, vv = np.linalg.svd(data - datamean)
    # Fitting
    line_vec = vv[0]
    for i in range(0, 20):
        t = (line_vec[0] * (probe_coord[i][0] - datamean[0]) + line_vec[1] * (probe_coord[i][1] - datamean[1]) + line_vec[2] * (probe_coord[i][2] - datamean[2]))
        probe_coord[i] = [datamean[0] + t * line_vec[0], datamean[1] + t * line_vec[1], datamean[2] + t * line_vec[2]]

        
plot()