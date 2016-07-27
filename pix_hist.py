import cv2
import numpy as np
from matplotlib import pyplot as plt
 
img = cv2.imread('./chip_images/scilla16.tiff',0)

img[img >= 255] = 0
img_array[(img_array > 75) & (img_array < 135)] = 0

plt.hist(img.ravel(),256,[0,256]) 
plt.show()
