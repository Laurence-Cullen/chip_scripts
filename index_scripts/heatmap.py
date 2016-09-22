import sys
import numpy as np
import matplotlib 
from matplotlib import pyplot as plt

def scrape(fid):
    x, y, z = [], [], []
    f = open(fid, 'r')
    for line in f.readlines()[1:]:
        e = line.split()
	x.append(float(e[0]))
	y.append(float(e[1]))
	z.append(float(e[2]))
    X = np.array(x)
    Y = np.array(y)
    Z = np.array(z)
    x = X.ravel()
    y = Y.ravel()
    z = Z.ravel()
    return x, y, z 

def main(fid):
    x, y, z = scrape(fid)
    y = -1*y
    print x.shape, y.shape, z.shape
    gridsize=4
    plt.subplot(111, aspect=1, axisbg='k')
    plt.scatter(x, y, c=z, s=100, alpha=1, marker='s')
    #plt.scatter(x, y, c=z, s=100, alpha=1)
    #plt.hexbin(x, y, C=z, gridsize=gridsize)
    #plt.hexbin(x, y, C=z, norm=matplotlib.colors.LogNorm(), gridsize=gridsize)
    plt.axis([x.min(), x.max(), y.min(), y.max()])
    cb = plt.colorbar()
    cb.set_label('value')

if __name__ == '__main__':
    main(sys.argv[1])
plt.show()
