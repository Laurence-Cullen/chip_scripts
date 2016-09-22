#!/bin/bash
# called as ./out_sift.sh -s data.out
#
# The function plots a map of the sample chip highlighting the cells with the highest number of
# crystals present
#
# -s, flag can be either -i for striping files by index or -s to strip by spot number
#

if [[ ! $# ==  2 ]]; then
	echo 'Usage: ./grid_plot.sh -s data.out'
	exit
fi

if [[ ( $1 != '-i' ) && ( $1 != '-s' ) ]]; then
	echo 'flag must be either -i for index sift or -s for spot sift'
	exit
fi

# checks that input file is of the correct type
if [[ ! $2 == *.out ]]; then
	echo 'incorrect file type, second arguement must be a .out file'
	exit
fi

# checks that .out file exists
if [[ ! -r $2 ]]; then
	#echo 'file not found'
	exit
fi

if [[ $1 == '-i' ]]; then

	# uses awk to scrape out filenames with non 0 index values and save them to temporary file
	awk -F'|' '( $9 > 0 ) && ( $2 !~ /image/) { print $2 $9 }' $2 > filter_list.tmp

	# counts number of files
	lines=($(wc -l filter_list.tmp))
	lines=$((lines-20))
	#echo -n $lines
	#echo ' files with non 0 index values'

fi

if [[ $1 == '-s' ]]; then

	# uses awk to scrape out files with over 100 spots and saves them to temporary file
	awk -F'|' '( $3 > 100 ) && ( $2 !~ /image/) { print $2 $3 }' $2 > filter_list.tmp

	# counts number of files
	lines=($(wc -l filter_list.tmp))
	lines=$((lines-20))
	#echo -n $lines
	#echo ' files with over 100 spots'

fi

python spot_map.py $1 $3

#echo $x

# clearing temporary file
#rm filter_list.tmp
