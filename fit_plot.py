import reduc
import intensity_plot
import os

def main(filename_in_pre, filename_in_post, plot_save_path):

	filename_out_pre = './pre_load_i_list.tmp'
	filename_out_post = './post_load_i_list.tmp'

	img_array, pix_scale, x_real_offset, y_real_offset, theta = reduc.meta_sweep(filename_in_pre, filename_out_pre)
	img_array, pix_scale, x_real_offset, y_real_offset, theta = reduc.meta_sweep(filename_in_post, filename_out_post)

	intensity_plot.main(filename_out_pre, filename_out_post, plot_save_path)

	os.remove(filename_out_pre)
	os.remove(filename_out_post)

	return 0