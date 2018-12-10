# Generate Points Coordinates

import csv, math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d as m3d

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
#     fig.suptitle('Iteration ' + str(count), fontsize=16)
    ax = plt.subplot(111, projection='3d')
    ax.scatter(xs, ys, zs, color='b')
    ax.scatter(xp, yp, zp, color='r')
#     ax.scatter(xs[1], ys[1], zs[1], color='r')
#     ax.scatter(xp[1], yp[1], zp[1], color='r')

    # plot plane
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]), np.arange(ylim[0], ylim[1]))
    Z = np.zeros(X.shape)
    for r in range(X.shape[0]):
        for c in range(X.shape[1]):
            Z[r,c] = param[0] * X[r,c] + param[1] * Y[r,c] + param[2]
    ax.plot_wireframe(X,Y,Z, color='k')

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
    

time_stamp = []
distance = []
with open('obs2.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count != 0:
            time_stamp.append(row[0])
            distance.append(row[1])
        line_count+=1

probe_coord = []
start_point = 5
while start_point > -5:
    probe_coord.append([0, -1, start_point])
    start_point -= 0.5

for itr in range(20):
    angle = 36*math.pi/180
    v = np.array([0, math.cos(25*math.pi/180), math.sin(25*math.pi/180)])
    R = np.array([[math.cos(angle), 0, math.sin(angle)],[0,1,0],[-math.sin(angle), 0, math.cos(angle)]])
    points = []
    for i in range(0,20):
        x = probe_coord[i][0] + (v[0]*float(distance[i]))
        y = probe_coord[i][1] + (v[1]*float(distance[i]))
        z = probe_coord[i][2] + (v[2]*float(distance[i]))
        points.append([x,y,z])
        v = R.dot(np.array(v))
    
    # Plane Fitting
    A = np.matrix([[i[0], i[1], 1] for i in points])
    B = np.matrix([[i[2]] for i in points])
    param = (A.T * A).I * A.T * B
    print(param)

    # 3D Projection onto the Plane
    a = float(param[0])
    b = float(param[1])
    c = float(param[2])

    # get a point on the plane
    # ref_point = [0, 0, c]
    proj_points = []
    for point in points:
        t = (a * (- point[0]) + b * (- point[1]) + (-1) * (c - point[2])) / (a * a + b * b + 1)
        proj_points.append([point[0] + t * a, point[1] + t * b, point[2] - t])
        
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





"""       
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
ax = plt.subplot(111, projection='3d')
ax.scatter(xs, ys, zs, color='b')
ax.scatter(xp, yp, zp, color='r')

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
ax.plot3D(*linepts.T)

ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()
"""        








"""
Test Points:
[(0.9830581524760388, 2.0057874871478694, 1.0359732192853757), (3.3539512110884253, 0.5374781161302757, -4.874892112521831), (1.2087037632785753, 4.428704921586718, -0.44314802334780273), (2.778949482134113, 5.075512840578294, 2.4693643205729967), (-2.3703231172900745, 6.468114673947321, 5.90965515540004), (0.9830581524760388, 2.0057874871478694, 1.0359732192853757)]
"""


"""
[[0.0, 1.936437229998746, 6.369283168039866],
[1.5475867093721334, 4.64629751323833, 6.630070367141281],
[1.8328183639062328, 3.1327635088871233, 4.595518786050506],
[1.5112712825191745, 2.4077172792578034, 3.008958193958355],
[1.6444661341963922, 4.999757550182623, 0.7365865440649633],
[9.377692939837038e-17, 2.3080234226837724, 0.957443344646447],
[-1.4358027576518348, 4.238459009071837, 0.023787043005360387],
[-2.9100010865528785, 5.561668378145345, 0.5544833309198113],
[-2.5924733436831584, 4.845685226386392, 1.842345651321439],
[-1.679243363620485, 5.126640640367754, 2.8112802057584365],
[-1.3154462425196064e-16, 3.640295869627648, 2.1638055001123813],
[0.9340170188184945, 2.4077172792578034, 0.7855641381141598],
[2.371409725229556, 4.347215943516235, -0.2294822724346528],
[2.548260619992438, 4.74599136981236, -2.3279800665702206],
[1.1352281319150321, 3.1418265867574906, -3.562507476378115],
[1.7136770385948779e-16, 5.045072939534455, -5.318863805810466],
[-1.4631277236279077, 4.338152865645868, -5.013822546141596],
[-1.4308845121724099, 2.2264557218504737, -3.9649225610394296],
[-2.1021140445678945, 3.7399897262016797, -3.3169817431920734],
[-0.9365011066345014, 2.4167803571281703, -3.2110168083270256]]
"""



"""
After Projection:
[(-2.154158443047887, 2.672317085249535, 10.943283373011965), (-0.5944592896396141, 5.378039648911057, 11.178351794702731), (0.6013638055890513, 3.553439436902984, 7.210309457709284), (0.8655570593280771, 2.6282990524457275, 4.380025860202357), (1.722762064444844, 4.973010957793423, 0.5703380482030743), (-0.13394332946949922, 2.3537796660185775, 1.2418499157718728), (-1.5897970575506621, 4.291064843839803, 0.3507685431707651), (-3.6067384363876904, 5.799680109268905, 2.0338901922122803), (-3.6754068246884213, 5.215625021585881, 4.14177630837228), (-2.9826328171601437, 5.571890174124936, 5.578812764419138), (-0.6702089311631146, 3.8692452548707723, 3.586883639237949), (1.0249380369725285, 2.376657843544347, 0.5925083501265264), (2.983219051402923, 4.1382163874071995, -1.5285584812214987), (3.9594016665022904, 4.263932924949383, -5.324305363259236), (2.8585829298081564, 2.5531131226610366, -7.2217671860073605), (2.0689286557383215, 4.338308344468371, -9.711892612934921), (0.27348809921080686, 3.7449093164254847, -8.701239855326726), (0.043778756282279785, 1.7226975159319275, -7.096126820384912), (-1.083263842099363, 3.391941354024391, -5.4803421264391154), (0.3299175451373805, 1.984160381025477, -5.9000479664015515)]
"""