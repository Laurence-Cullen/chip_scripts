#!/bin/bash

source clear.txt

ls *.py* > python_scripts.tmp

while IFS='' read -r line || [[ -n "$line" ]]; do

	output=$(basename "$line" .py)
    extension='.pdf'
    prefix='./PDFs/'
    output=$prefix$output$extension

    echo PDF saved as: $output

	enscript --color=10 --font="Ariel8" -Epython $line -o - | ps2pdf - $output
    echo "$line saved as PDF"

done < python_scripts.tmp

rm python_scripts.tmp