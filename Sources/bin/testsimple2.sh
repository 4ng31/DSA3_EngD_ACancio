#!/bin/bash

BASENAME1=/home/taller-dis1/Angel/CUDA_test/MG11_NET4_2017_038_DD_E1_172242_
BASENAME2=/home/taller-dis1/Angel/CUDA_test/MG12_NET4_2017_038_DD_E1_172247_
BASENAME3=/home/taller-dis1/Angel/CUDA_test/MG13_NET4_2017_038_DD_E1_172251_

for i in `seq -w 0008 10 0358`; do 	#ON
	FILE1=${BASENAME1}${i}-new
	FILE2=${BASENAME2}${i}-new
	FILE3=${BASENAME3}${i}-new
	if [[ -e $FILE1 && -e $FILE2 && -e $FILE3 ]]; then
		python simpledataproc1.py -q 16 -i1 $FILE1 -i2 $FILE2 -i3 $FILE3 -o result_simple1.txt >> simple_resultE1_on.log ;
	else 
	    echo "File does not exist"
	fi 
done
	
for i in `seq -w 0001 10 0361`; do 	#OFF
	FILE1=${BASENAME1}${i}-new
	FILE2=${BASENAME2}${i}-new
	FILE3=${BASENAME3}${i}-new
	if [[ -e $FILE1 && -e $FILE2 && -e $FILE3 ]]; then
		python simpledataproc1.py -q 16 -i1 $FILE1 -i2 $FILE2 -i3 $FILE3  -o result_simple1.txt >> simple_resultE1_off.log ;
	else 
	    echo "File does not exist"
	fi 
done

BASENAME1=/home/taller-dis1/Angel/CUDA_test/MG11_NET4_2017_038_DD_E2_172242_
BASENAME2=/home/taller-dis1/Angel/CUDA_test/MG12_NET4_2017_038_DD_E2_172247_
BASENAME3=/home/taller-dis1/Angel/CUDA_test/MG13_NET4_2017_038_DD_E2_172251_

for i in `seq -w 0008 10 0358`; do 	#ON
	FILE1=${BASENAME1}${i}-new
	FILE2=${BASENAME2}${i}-new
	FILE3=${BASENAME3}${i}-new
	if [[ -e $FILE1 && -e $FILE2 && -e $FILE3 ]]; then
		python simpledataproc1.py -q 16 -i1 $FILE1 -i2 $FILE2 -i3 $FILE3  -o result_simple1.txt >> simple_resultE2_on.log ;
	else 
	    echo "File does not exist"
	fi 
done
 	
for i in `seq -w 0001 10 0361`; do 	#OFF
	FILE1=${BASENAME1}${i}-new
	FILE2=${BASENAME2}${i}-new
	FILE3=${BASENAME3}${i}-new
	if [[ -e $FILE1 && -e $FILE2 && -e $FILE3 ]]; then
		python simpledataproc1.py -q 16 -i1 $FILE1 -i2 $FILE2 -i3 $FILE3  -o result_simple1.txt >> simple_resultE2_off.log ;
	else 
	    echo "File does not exist"
	fi 
done

