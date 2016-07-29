import cv2
import numpy as np
from PIL import Image
from numba import jit
import cv2

"""
This script takes the local standard deviation of an image and saves it to
a new one. 
"""

def main(filename, box_size):
	img = cv2.imread(filename, 0)
	
	shape = np.shape(img)

	x_pix_max = shape[0]
	y_pix_max = shape[1]

	#box_size = 3 # default value of 3
	box_length = (2 * box_size) + 1

	std_dev_map = process(img, box_length, box_size, x_pix_max, y_pix_max)

	std_dev_map = np.asarray(std_dev_map)

	std_dev_map = np.uint8(std_dev_map)

	thresh = np.zeros((x_pix_max, y_pix_max))

	thresh_value = np.percentile(std_dev_map, 80)

	std_dev_map[std_dev_map >= 255] = 255
	std_dev_map[std_dev_map < thresh_value] = 0


	std_dev_map = np.uint8(std_dev_map)

	std_dev_img = Image.fromarray(np.uint8(std_dev_map))

	filename_out = ('./images/std_dev_map.png')

  	std_dev_img.save(filename_out)
  	print('standard deviation map saved')

  	return std_dev_map


@jit(nopython=True)
def process(img, box_length, box_size, x_pix_max, y_pix_max):

	std_dev_map = np.zeros((x_pix_max, y_pix_max))

	for x in xrange(0, x_pix_max):
		for y in xrange(0, y_pix_max):

			box = np.zeros((box_length, box_length))

			if((x >= box_size) and (x < x_pix_max - box_size) and (y >= box_size) \
				and (y < y_pix_max - box_size)):

				for x_box in xrange(-box_size, box_size):
					for y_box in xrange(-box_size, box_size):
						box[x_box + box_size][y_box + box_size] = img[x + x_box][y + y_box]

				if(np.mean(box) != 0):
					std_dev_map[x][y] = (150 * np.std(box)) / np.mean(box)
				else:
					std_dev_map[x][y] = 0

	return std_dev_map