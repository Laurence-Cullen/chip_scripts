import reduc
import intensity_plot
import os

def main(off_zero_filename_in, on_zero_filename_in, plot_save_path):

	off_zero_filename_out = './off_zero_i_list.tmp'
	on_zero_filename_out = './on_zero_i_list.tmp'

	img_array, pix_scale, x_real_offset, y_real_offset, theta = \
	reduc.meta_sweep(off_zero_filename_in, off_zero_filename_out)
	
	img_array, pix_scale, x_real_offset, y_real_offset, theta = \
	reduc.meta_sweep(on_zero_filename_in, on_zero_filename_out, on_zero=1)

	intensity_plot.main(off_zero_filename_out, on_zero_frame_filename_out, plot_save_path)

	os.remove(off_zero_filename_out)
	os.remove(on_zero_filename_out)

	return 0