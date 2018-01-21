from PIL import Image
import numpy as np
import math
import visual_map
import watershed
import variance_map
from numba import jit


@jit(nopython=True)
def rotate(x, y, rot_matrix):
    col_vec = np.zeros(2)
    col_vec[0] = x
    col_vec[1] = y
    col_vec = np.dot(rot_matrix, col_vec)

    return col_vec[0], col_vec[1]


# generates a mask from the theoretical layout of a chip
def chip_mask_gen(x_pix_max, y_pix_max, cell_real_size,
                  x_real_offset, y_real_offset, pix_scale, theta, x, y, z):
    chip_mask = chip_mask_crunch(x_pix_max, y_pix_max, cell_real_size,
                                 x_real_offset, y_real_offset, pix_scale, theta, x, y, z)

    chip_mask = np.flipud(chip_mask)
    chip_mask = np.rot90(chip_mask, 3)

    return chip_mask


@jit(nopython=True)
def chip_mask_crunch(x_pix_max, y_pix_max, cell_real_size,
                     x_real_offset, y_real_offset, pix_scale, theta, x, y, z):
    # final cell index
    i_max = 11664

    i_half = 5832

    # initializing mask array
    mask = np.zeros((x_pix_max, y_pix_max))

    cell_pix_size_float = cell_real_size * pix_scale  # width of cell in pixels
    cell_pix_size_int = int(math.ceil(cell_pix_size_float))

    x_pix = np.zeros(i_max)
    y_pix = np.zeros(i_max)

    # location of cells in terms of image pixels
    for i in xrange(0, 11664):
        x_pix[i] = round((x[i] + x_real_offset) * pix_scale)
        y_pix[i] = round((y[i] + y_real_offset) * pix_scale)

    x_mid = x_pix[i_half]
    y_mid = y_pix[i_half]

    rot_matrix = np.zeros((2, 2))
    rot_matrix[0][0] = math.cos(theta)
    rot_matrix[1][1] = math.cos(theta)
    rot_matrix[1][0] = - math.sin(theta)
    rot_matrix[0][1] = math.sin(theta)

    # accounting for x, y shift of the middle of mask so rotation only takes 
    # place around centre of chip
    x, y = rotate(x_mid, y_mid, rot_matrix)
    delt_x = x - x_mid
    delt_y = y - y_mid

    for i in xrange(0, i_max):
        for r_x in xrange(-cell_pix_size_int, cell_pix_size_int):
            for r_y in xrange(-cell_pix_size_int, cell_pix_size_int):

                if math.sqrt(r_x ** 2 + r_y ** 2) <= cell_pix_size_float:

                    x = int(round(x_pix[i] + r_x))  # temporary x
                    y = int(round(y_pix[i] + r_y))  # temporary y

                    x, y = rotate(x, y, rot_matrix)

                    # correcting for non centred rotation
                    x = int(round(x - delt_x))
                    y = int(round(y - delt_y))

                    if 0 <= x < x_pix_max and 0 <= y < y_pix_max:
                        mask[int(x)][int(y)] = z[int(i)]

    return mask


@jit(nopython=True)
def rect_cent_mask_gen(x_pix_max, y_pix_max, pix_scale, real_circ_rad, good_rect_log, cent_cords):
    pix_circ_rad = int(round(real_circ_rad * pix_scale))

    mask = np.zeros((x_pix_max, y_pix_max))

    length = good_rect_log.size

    for count in xrange(1, length):
        for x in xrange(-pix_circ_rad, pix_circ_rad):
            for y in xrange(-pix_circ_rad, pix_circ_rad):

                # only masking for rectangles with adjacent neighbours (horizontal and vertical) 
                if good_rect_log[count] == 1:
                    if math.sqrt(x ** 2 + y ** 2) <= pix_circ_rad:

                        if (cent_cords[count][1] + x >= 0) and (cent_cords[count][1] + x < x_pix_max) \
                                and (cent_cords[count][0] + y >= 0) and (cent_cords[count][0] + y < y_pix_max):
                            mask[cent_cords[count][1] + x][cent_cords[count][0] + y] = 1.0

    return mask


# returns the index of an iterable given its value
@jit(nopython=True)
def index(value, min_index, step):
    return int(round((value - min_index) / step) - 1)


# returns the value of an iterable for a given index
@jit(nopython=True)
def de_index(i, min_index, step):
    return ((i + 1) * step) + min_index


# @jit(nopython=True)
def mask_image(rect_mask, img_array):
    return img_array.astype(np.float64) * rect_mask.astype(np.float64)


# Search mask generation parameter space to find optimal fitting
# @jit
def sweep(filename, x_r_off_min, x_r_off_max, y_r_off_min, y_r_off_max, real_trans_step_x, real_trans_step_y,
          cell_real_size, x, y, z, cent_cords, good_rect_log, img_array, rect_mask, pix_scale, theta, std_dev_map,
          sweep_type=0):

    print('in sweep')

    # stops searching of space outside of this zone
    x_hard_min = 8.0
    x_hard_max = 16
    y_hard_min = 0
    y_hard_max = 5.2

    print('before shape')

    x_pix_max, y_pix_max = np.shape(img_array)

    print('after shape')

    # values to iterate x_real_offset and y_real_offset over
    x_r_off_iter = np.arange(x_r_off_min, x_r_off_max, real_trans_step_x)
    y_r_off_iter = np.arange(y_r_off_min, y_r_off_max, real_trans_step_y)

    print('iterables created')

    # calculating number of solutions
    ind_x_max = 1 + index(x_r_off_max, x_r_off_min, real_trans_step_x)
    ind_y_max = 1 + index(y_r_off_max, y_r_off_min, real_trans_step_y)

    print('calculating array dimension sizes')

    sums = np.zeros((ind_x_max, ind_y_max))
    sums_omni = np.zeros((ind_x_max, ind_y_max))

    print('about to start loop')

    # iterating over x and y offset values for chip mask
    for x_real_offset in x_r_off_iter:
        for y_real_offset in y_r_off_iter:

            print('x offset = %f' % x_real_offset)
            print('y offset = %f' % y_real_offset)

            sum_current = 0
            # sum_current_rect = 0
            non_zero_pixels = 0
            sum_current_std_dev = 0

            if ((x_real_offset > x_hard_min) & (x_real_offset < x_hard_max) &
                    (y_real_offset > y_hard_min) & (y_real_offset < y_hard_max)):

                # creating mask of chip
                chip_mask = chip_mask_gen(y_pix_max, x_pix_max, cell_real_size, x_real_offset,
                                          y_real_offset, pix_scale, theta, x, y, z)

                # convolving chip mask with image
                chip_conv_img_array = img_array * chip_mask
                sum_current = np.sum(chip_conv_img_array)

                # sweep using a larger cell size and against the good rect mask to
                # ensure a good city block match
                if sweep_type == 1:
                    # convolving chip mask convolved image with known city block mask
                    conv_rect_img_array = chip_conv_img_array * rect_mask

                    non_zero_pixels = np.count_nonzero(conv_rect_img_array)
                    print('%d non zero pixels' % non_zero_pixels)

                    # convolving std_dev_map with chip_mask 
                    conv_std_dev_img_array = std_dev_map * chip_mask

                    # convert to non zero pix count!!
                    sum_current_std_dev = np.count_nonzero(conv_std_dev_img_array)

                    print('%d non zero std dev pixels' % sum_current_std_dev)

            ind_x = index(x_real_offset, x_r_off_min, real_trans_step_x)
            ind_y = index(y_real_offset, y_r_off_min, real_trans_step_y)

            sums[ind_x, ind_y] = sum_current

            sums_omni[ind_x, ind_y] = non_zero_pixels + sum_current_std_dev

            print('sum current = %f' % sums[ind_x, ind_y])
            print('sum_omni = %f' % sums_omni[ind_x, ind_y])

    if sweep_type == 1:

        # returns the indices of the sums element with the highest value
        i, j = np.unravel_index(sums_omni.argmax(), sums_omni.shape)
        print(i, j)
        x_real_offset = de_index(i, x_r_off_min, real_trans_step_x)
        y_real_offset = de_index(j, y_r_off_min, real_trans_step_y)

        print('%f pixels per mm, x offset of %f mm and y offset of %f mm' % (pix_scale, x_real_offset, y_real_offset))

        # calculating and displaying the convolution of the best fit mask with the input image
        chip_mask = chip_mask_gen(y_pix_max, x_pix_max, cell_real_size, x_real_offset,
                                  y_real_offset, pix_scale, theta, x, y, z)

        img_array = img_array * chip_mask * rect_mask

        # loading array into image and saving
        img = Image.fromarray(np.uint8(img_array))
        img.save('./images/type1_fit.png')

    elif sweep_type == 0:

        print('sweep_type = %d' % sweep_type)

        print('determining best fit from sweep type 0')

        # returns the indicies of the sums element with the highest value
        i, j = np.unravel_index(sums.argmax(), sums.shape)

        x_real_offset = de_index(i, x_r_off_min, real_trans_step_x)
        y_real_offset = de_index(j, y_r_off_min, real_trans_step_y)

        print('%f pixels per mm, x offset of %f mm and y offset of %f mm' %
              (pix_scale, x_real_offset, y_real_offset))

        # calculating and displaying the convolution of the best fit mask with the input image

        chip_mask = chip_mask_gen(y_pix_max, x_pix_max, cell_real_size, x_real_offset,
                                  y_real_offset, pix_scale, theta, x, y, z)

        img_array *= chip_mask

        img = Image.fromarray(np.uint8(img_array))
        img.save('./images/type0_fit.png')
        print('image saved')

    # returns best fit mask generation parameters and image data
    return img_array, pix_scale, x_real_offset, y_real_offset, theta


def meta_sweep(filename, filename_out):
    # opening image and converting to greyscale
    img_array = np.asarray(Image.open(filename).convert('L'))
    img_array.flags.writeable = True  # making array readable

    x, y, z = visual_map.main()  # get real space position of cells on chip
    z[z == 2] = 0
    z[z == 7] = 0
    z[z == 4] = 1

    # get fitting information from feature recognition code
    # format of angle_mean, angle_std_err, pix_scale_mean, pix_scale_std_err, count
    # getting fit which gives lowest pixel scale and angle error
    data, cent_cords_null, good_rect_log_null = watershed.error_minimize(filename, mode=0)

    # getting fit which yields highest number of rectangles
    data_null, cent_cords, good_rect_log = watershed.error_minimize(filename, mode=1)

    theta = - math.radians(data[0])
    pix_scale = data[2]

    print('theta = %f rads' % theta)
    print('pix scale = %f pixels per mm' % pix_scale)

    std_dev_box_size = 2
    std_dev_map = variance_map.main(filename, std_dev_box_size)

    print('exited variance_map.py')

    x_pix_max, y_pix_max = np.shape(img_array)

    real_circ_rad = 1.05  # radius of circle around identified rectangles to be masked (mm)
    rect_mask = rect_cent_mask_gen(x_pix_max, y_pix_max, pix_scale, real_circ_rad, good_rect_log, cent_cords)

    # correcting for orientation
    # rect_mask = np.flipud(rect_mask)
    # rect_mask = np.rot90(rect_mask, 3)

    # loading array into image and saving
    rect_mask_img = Image.fromarray(np.uint8(rect_mask * 200))
    rect_mask_img.save('./images/rect_mask.png')

    # TODO fix error

    print('rect_mask shape = %s, img_array shape = %s' % (str(np.shape(rect_mask)), str(np.shape(img_array))))

    # masking img_array with the fitted city block rectangles
    img_array_perm = mask_image(rect_mask, img_array)

    print('completed image masking')

    # loading array into image and saving
    smart_clean_img = Image.fromarray(np.uint8(img_array_perm))
    smart_clean_img.save('./images/masked_image.png')

    # default cell radius (mm)
    cell_real_size = 0.03

    sweep_num_max = 8

    # setting x and y offset iteration parameters (mm)
    x_r_off_min = 10.5
    x_r_off_max = 13

    y_r_off_min = 1.5
    y_r_off_max = 4

    # loading sweep pattern
    sweep_data = sweep_pattern()

    for sweep_num in xrange(1, sweep_num_max):
        sweep_type = 0
        print('sweep number = %d' % sweep_num)

        if sweep_num == 5:
            print('sweep type of 1')
            sweep_type = 1

        print(x_r_off_min, x_r_off_max, y_r_off_min, y_r_off_max,
              sweep_data[sweep_num - 1][1], sweep_data[sweep_num - 1][2])

        img_array = img_array_perm

        img_array, pix_scale, x_real_offset, y_real_offset, theta = sweep(filename, x_r_off_min, x_r_off_max,
                                                                          y_r_off_min, y_r_off_max,
                                                                          sweep_data[sweep_num - 1][1],
                                                                          sweep_data[sweep_num - 1][2],
                                                                          cell_real_size, x, y, z, cent_cords,
                                                                          good_rect_log, img_array, rect_mask,
                                                                          pix_scale, theta, std_dev_map, sweep_type)

        print('after sweep of sweep_num %d of sweep_type %d' % (sweep_num, sweep_type))

        if sweep_num <= sweep_num_max - 2:
            x_r_off_min = x_real_offset - sweep_data[sweep_num][0] * sweep_data[sweep_num][1]
            x_r_off_max = x_real_offset + sweep_data[sweep_num][0] * sweep_data[sweep_num][1]

            y_r_off_min = y_real_offset - sweep_data[sweep_num][0] * sweep_data[sweep_num][2]
            y_r_off_max = y_real_offset + sweep_data[sweep_num][0] * sweep_data[sweep_num][2]

    i_list = read_out(img_array_perm, cell_real_size, x_real_offset, y_real_offset, pix_scale, theta, x, y)

    np.savetxt(filename_out, i_list)

    print('i_list.txt saved')

    return img_array, pix_scale, x_real_offset, y_real_offset, theta


@jit
def sweep_pattern():
    # translational offset iteration step (mm), 0.125 is spacing between cells
    real_trans_step_1 = 0.25

    # size of search area in second sweep
    steps_2 = 5
    real_trans_step_2 = 0.0125

    # size of search area in third sweep 
    steps_3 = 6
    real_trans_step_3 = 0.125

    # size of search area in fourth sweep
    steps_4 = 6
    real_trans_step_4 = 0.125

    # size of search area in fifth sweep by city block
    steps_5 = 3
    real_trans_step_x_5 = 2.2
    real_trans_step_y_5 = 2.5

    # size of search area in sixth sweep
    steps_6 = 5
    real_trans_step_x_6 = 0.125
    real_trans_step_y_6 = 0.125

    # size of search area in seventh sweep
    steps_7 = 5
    real_trans_step_x_7 = 0.0125
    real_trans_step_y_7 = 0.0125

    # stores the steps, real_trans_step_x, real_trans_step_y
    sweep_data = [[0, real_trans_step_1, real_trans_step_1],
                  [steps_2, real_trans_step_2, real_trans_step_2],
                  [steps_3, real_trans_step_3, real_trans_step_3],
                  [steps_4, real_trans_step_4, real_trans_step_4],
                  [steps_5, real_trans_step_x_5, real_trans_step_y_5],
                  [steps_6, real_trans_step_x_6, real_trans_step_y_6],
                  [steps_7, real_trans_step_x_7, real_trans_step_y_7]]

    return sweep_data


# !!!!!!!!!!!!!! sometimes segfaults!
# reads out summed values for for each cell
def read_out(img_array, cell_real_size, x_real_offset, y_real_offset, pix_scale, theta, x, y):
    # putting image array into correct frame
    img_array = np.rot90(img_array, 1)  # maybe
    img_array = np.flipud(img_array)

    i_list = read_out_crunch(img_array, cell_real_size, x_real_offset, y_real_offset, pix_scale, theta, x, y)

    return i_list


# @jit(nopython=True)
def read_out_crunch(img_array, cell_real_size, x_real_offset, y_real_offset, pix_scale, theta, x, y):
    # final cell index
    i_max = 11664
    i_half = 5832

    x_pix_max = 1292
    y_pix_max = 964

    # [cell number][total intensity, number of pixels for cell]
    i_list = np.zeros((i_max, 2))

    cell_pix_size_float = cell_real_size * pix_scale  # width of cell in pixels
    cell_pix_size_int = int(math.ceil(cell_pix_size_float))

    x_pix = np.zeros(i_max)
    y_pix = np.zeros(i_max)

    # location of cells in terms of image pixels
    for i in xrange(0, 11664):
        x_pix[i] = round((x[i] + x_real_offset) * pix_scale)
        y_pix[i] = round((y[i] + y_real_offset) * pix_scale)

    x_mid = x_pix[i_half]
    y_mid = y_pix[i_half]

    rot_matrix = np.zeros((2, 2))
    rot_matrix[0][0] = math.cos(theta)
    rot_matrix[1][1] = math.cos(theta)
    rot_matrix[1][0] = - math.sin(theta)
    rot_matrix[0][1] = math.sin(theta)

    # accounting for x, y shift of the middle of mask so rotation only takes 
    # place around centre of chip
    x, y = rotate(x_mid, y_mid, rot_matrix)
    delt_x = x - x_mid
    delt_y = y - y_mid

    for i in xrange(0, i_max):
        for r_x in xrange(-cell_pix_size_int, cell_pix_size_int):
            for r_y in xrange(-cell_pix_size_int, cell_pix_size_int):

                if math.sqrt(r_x ** 2 + r_y ** 2) <= cell_pix_size_float:

                    x = int(round(x_pix[i] + r_x))  # temporary x
                    y = int(round(y_pix[i] + r_y))  # temporary y

                    x, y = rotate(x, y, rot_matrix)

                    # correcting for non centred rotation
                    x = int(round(x - delt_x))
                    y = int(round(y - delt_y))

                    if 0 <= x < x_pix_max and 0 <= y < y_pix_max:
                        i_list[int(i)][0] = i_list[int(i)][0] + img_array[int(x)][int(y)]
                        i_list[int(i)][1] += 1

                    else:
                        pass
    return i_list


def main():
    meta_sweep('./chip_images/A_empty2.tiff', 'reduc_out.txt')


if __name__ == '__main__':
    main()
