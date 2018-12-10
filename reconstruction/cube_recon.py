import csv, math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as m3d


"""
Helper Functions
"""

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
#     fig.suptitle('Iteration ' + str(count), fontsize=16)
    ax = plt.subplot(111, projection='3d')
    ax.scatter(xs, ys, zs, color='b')
    ax.scatter(xp, yp, zp, color='r')
#     ax.scatter(xs[1], ys[1], zs[1], color='r')
#     ax.scatter(xp[1], yp[1], zp[1], color='r')


#     # plot plane
#     xlim = ax.get_xlim()
#     ylim = ax.get_ylim()
#     X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]), np.arange(ylim[0], ylim[1]))
#     Z = np.zeros(X.shape)
#     for r in range(X.shape[0]):
#         for c in range(X.shape[1]):
#             Z[r,c] = param[0] * X[r,c] + param[1] * Y[r,c] + param[2]
#     ax.plot_wireframe(X,Y,Z, color='k')


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
    plt.show()

    
def findDistance(point, plane):
    a = float(plane[0])
    b = float(plane[1])
    c = float(plane[2])
    return abs(a * point[0] + b * point[1] - point[2] + c) / math.sqrt(a * a + b * b + 1)
    

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

for itr in range(6):
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
    
    print(points)
    
    if itr == 0:
        # Clustering
        clusters = [[],[],[],[],[],[]] # +x, -x, +y, -y, +z, -z
        if itr == 0:
            centroid = [sum([i[0] for i in points]) / len(points), sum([i[1] for i in points]) / len(points), sum([i[2] for i in points]) / len(points)]
            for i in range(40):
                min_cluster = 0
                min_dist = float("inf")
                if abs(points[i][0] - (centroid[0] + 10)) < min_dist:
                    min_dist = abs(points[i][0] - (centroid[0] + 10))
                    min_cluster = 0
                if abs(points[i][0] - (centroid[0] - 10)) < min_dist:
                    min_dist = abs(points[i][0] - (centroid[0] - 10))
                    min_cluster = 1
                if abs(points[i][1] - (centroid[1] + 10)) < min_dist:
                    min_dist = abs(points[i][1] - (centroid[1] + 10))
                    min_cluster = 2
                if abs(points[i][1] - (centroid[1] - 10)) < min_dist:
                    min_dist = abs(points[i][1] - (centroid[1] - 10))
                    min_cluster = 3
                if abs(points[i][2] - (centroid[2] + 10)) < min_dist:
                    min_dist = abs(points[i][2] - (centroid[2] + 10))
                    min_cluster = 4
                if abs(points[i][2] - (centroid[2] - 10)) < min_dist:
                    min_dist = abs(points[i][2] - (centroid[2] - 10))
                    min_cluster = 5
                clusters[min_cluster].append(i)
        else:
            for i in range(40):
                min_cluster = 0
                min_dist = float("inf")
                for j in range(len(cube)):
                    cur_dist = findDistance(points[i], cube[j])
                    if cur_dist < min_dist:
                        min_dist = cur_dist
                        min_cluster = j
                clusters[min_cluster].append(i)
            
        print(clusters)
    
    cube = []
    proj_points = [[] for i in range(40)]
    for pts in clusters:
        if not pts:
            continue
            
        # Plane Fitting
        A = np.matrix([[points[i][0], points[i][1], 1] for i in pts])
        B = np.matrix([[points[i][2]] for i in pts])
        param = (A.T * A).I * A.T * B
        cube.append(param)

        # 3D Projection onto the Plane
        a = float(param[0])
        b = float(param[1])
        c = float(param[2])

        # get a point on the plane
        # ref_point = [0, 0, c]
        for i in pts:
            t = (a * (- points[i][0]) + b * (- points[i][1]) + (-1) * (c - points[i][2])) / (a * a + b * b + 1)
            proj_points[i] = [points[i][0] + t * a, points[i][1] + t * b, points[i][2] - t]

    # move the probe positions
    for i in range(0, 20):
        x_new = probe_coord[i][0] + ((proj_points[2*i][0] - points[i][0]) + (proj_points[2*i + 1][0] - points[i][0])) / 2
        y_new = probe_coord[i][1] + ((proj_points[2*i][1] - points[i][1]) + (proj_points[2*i + 1][1] - points[i][1])) / 2
        z_new = probe_coord[i][2] + ((proj_points[2*i][2] - points[i][2]) + (proj_points[2*i + 1][2] - points[i][2])) / 2
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