#!/bin/bash

#for i in `seq -w 0008 10 0358`; do 	#ON
#	python dataproc-multi.py -q 16 -i1 /home/taller-dis1/Angel/CUDA_test/MG11_NET4_2017_038_DD_E1_172242_${i}-new -i2 /home/taller-dis1/Angel/CUDA_test/MG12_NET4_2017_038_DD_E1_172247_${i}-new -i3 /home/taller-dis1/Angel/CUDA_test/MG13_NET4_2017_038_DD_E1_172251_${i}-new >> resultE1_on.log ;
#done
#
# 	
#for i in `seq -w 0001 10 0361`; do 	#OFF
#	python dataproc-multi.py -q 16 -i1 /home/taller-dis1/Angel/CUDA_test/MG11_NET4_2017_038_DD_E1_172242_${i}-new -i2 /home/taller-dis1/Angel/CUDA_test/MG12_NET4_2017_038_DD_E1_172247_${i}-new -i3 /home/taller-dis1/Angel/CUDA_test/MG13_NET4_2017_038_DD_E1_172251_${i}-new >> resultE1_off.log ;
#done
#
#for i in `seq -w 0008 10 0358`; do 	#ON
#	python dataproc-multi.py -q 16 -i1 MG11_NET4_2017_038_DD_E2_172242_${i}-new -i2 /home/taller-dis1/Angel/CUDA_test/MG12_NET4_2017_038_DD_E2_172247_${i}-new -i3 /home/taller-dis1/Angel/CUDA_test/MG13_NET4_2017_038_DD_E2_172251_${i}-new >> resultE2_on.log ;
#done

 	
for i in `seq -w 0001 10 0361`; do 	#OFF
	file="/home/taller-dis1/Angel/CUDA_test/MG11_NET4_2017_038_DD_E2_172242_${i}-new"
	if [ -e "$file" ]; then
		python dataproc-multi.py -q 16 -i1 /home/taller-dis1/Angel/CUDA_test/MG11_NET4_2017_038_DD_E2_172242_${i}-new -i2 /home/taller-dis1/Angel/CUDA_test/MG12_NET4_2017_038_DD_E2_172247_${i}-new -i3 /home/taller-dis1/Angel/CUDA_test/MG13_NET4_2017_038_DD_E2_172251_${i}-new >> resultE2_off.log ;
	else 
	    echo "File does not exist"
	fi 
done



