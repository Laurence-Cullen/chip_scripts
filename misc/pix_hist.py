import cv2
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image
 
img = cv2.imread('./images/std_dev_map_box_2.png',0)

img[img >= 255] = 0
img[(img >=100) & (img <= 120)] = 0

# loading array into image and saving
img = Image.fromarray(np.uint8(img))
img.save('./images/filter_test.png')

#plt.hist(img.ravel(),256,[0,256]) 
#plt.show()
