import numpy as np
import math
import PIL.Image as Image
import numpy.linalg as la


# creates mask that blocks the centre and extremities of fourier transform
# leaving only city block scale signal
def fourier_mask(shape):
    # read dimensions of image to create mask for
    x_pix = int(shape[0])
    y_pix = int(shape[1])

    print('input image has dimensions of x = %d and y = %d' % (x_pix, y_pix))

    # set size of mask (circular shape)
    mask_inner_radius = x_pix / 13
    mask_outer_radius = x_pix / 4
    x_cent = x_pix / 2
    y_cent = y_pix / 2

    # initialising zeroed array to hold mask
    f_mask = np.zeros((x_pix, y_pix))

    # cycling over all pixels in the zeroed array
    for x in xrange(0, x_pix):
        for y in xrange(0, y_pix):
            r = math.sqrt((x - x_cent) ** 2 + (y - y_cent) ** 2)

            # setting circular region larger than mask_inner_radius and less than
            # mask_outer_radius to 1, all other regions of array left at 0
            if (r > mask_inner_radius) & (r < mask_outer_radius):
                f_mask[x][y] = 1

    # mask saved as image for debugging purposes, maybe remove?
    img = Image.fromarray(np.uint8(f_mask))
    img.save('./images/mask.png')
    print('mask saved to disk')

    return f_mask


def threshold_tweak(ftrans, max_peak, peaks):
    thresh_step = 0.0001

    # setting threshold values to iterate over
    thresh_iter = np.arange(0.001, 0.2, thresh_step)

    for thresh in thresh_iter:
        ftrans_temp = ftrans
        ftrans_temp[ftrans_temp < (max_peak * thresh)] = 0

        # uncomment to make function verbose
        # print('%d non zero pixels detected at threshold of %f %% of peak value') \
        # % (np.count_nonzero(ftrans_temp), thresh * 100)

        if np.count_nonzero(ftrans_temp) == peaks:
            print('%d peaks found when the threshhold = %f %% of the max peak \
                intensity') % (peaks, thresh * 100)
            return ftrans_temp

        if np.count_nonzero(ftrans_temp) < peaks:
            print('threshold iteration has skipped over %d peak values, try again \
                with a finer threshold step') % peaks

            return 0

    print('no good threshold found, sorry...')

    return 0


# extracts the angle of inclination of the chip from a filtered 2dfft
def find_angle(clean_fft, peaks):
    args = np.zeros((peaks, 2))

    # fills array args up with the indicies of non zero pixels
    for peak in xrange(0, peaks):
        args[peak] = np.unravel_index(np.argmax(clean_fft), np.shape(clean_fft))

        print('peak %d has intensity of %f' % (peak + 1, np.amax(clean_fft)))
        print('and position of [%d, %d]' % (args[peak][0], args[peak][1]))

        clean_fft[int(args[peak][0])][int(args[peak][1])] = 0

    # claculate vector between two identified pixels
    vector = np.zeros(2)
    vector[0] = args[0][0] - args[1][0]
    vector[1] = args[0][1] - args[1][1]

    # finding magnitude of vector
    vec_mag = math.sqrt(vector[0] ** 2 + vector[1] ** 2)

    print('vec_mag = %f' % vec_mag)

    # setting reference vertical vector
    vert_vect = np.array([0, 1])

    # computing angle between calculated and reference vector
    angle = vector_angle(vector, vert_vect)

    deg_angle = angle * 360 / (2 * math.pi)
    print('angle = %f degrees before quadrant correction' % deg_angle)

    # finding quadrant in which the calculated angle is closest to reference values of
    # 0, pi/2, pi and (3 * pi) / 4
    quadrant_angles = np.array([0.0, math.pi / 2.0, math.pi, - math.pi / 2.0])
    quadrant_delta = np.array([0.0, 0.0, 0.0, 0.0])

    for quadrant in xrange(0, 4):
        quadrant_delta[quadrant] = angle - quadrant_angles[quadrant]

    quadrant = int(np.argmin(np.fabs(quadrant_delta)))

    angle = quadrant_delta[quadrant]

    deg_angle = angle * 360 / (2 * math.pi)
    print('chip is rotated  %f degrees counter clockwise' % deg_angle)

    return angle, vec_mag


# returns the angle in radians between vectors v1 and v2
def vector_angle(v1, v2):
    cosang = np.dot(v1, v2)
    sinang = la.norm(np.cross(v1, v2))

    return np.arctan2(sinang, cosang)


# attempts to determine the orientation of a chip image
# (clockwise rotation in radians)
def orient(filename):
    img_array = np.asarray(Image.open(filename).convert('L'))
    print('image loaded')

    shape = np.shape(img_array)

    # performing fourier transform
    ftrans = np.fft.fft2(img_array)

    # gets mask for fourier transform
    f_mask = fourier_mask(shape)

    # sets peak intensity to be at the centre of the image
    ftrans = np.fft.fftshift(ftrans)

    # determine peak of fourier transform
    max_peak = np.max(np.abs(ftrans))

    # convolve mask with fourier data
    masked_ftrans = ftrans * f_mask

    # image of mask loaded into image and saved
    img = Image.fromarray(np.uint8(masked_ftrans))
    img.save('./images/masked_ftrans.png')
    print('masked ftrans saved')

    # number of peaks that the threshold will be tweaked to find (2 by default),
    # different angle determination method required
    # with more than 2 peaks
    peaks = 2

    masked_ftrans = threshold_tweak(masked_ftrans, max_peak, peaks)

    # log scale data
    abs_data = 1 + np.abs(masked_ftrans)
    c = 255.0 / np.log(1 + max_peak)
    log_data = c * np.log(abs_data)

    # array loaded into image and saved
    img = Image.fromarray(np.uint8(log_data))
    img.save('./images/orient.png')
    print('image saved to disk')

    theta, vec_mag = find_angle(log_data, peaks)

    return theta, vec_mag
