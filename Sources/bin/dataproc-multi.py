
# Antena Data Processor 
import numpy as np
import sys,os
import argparse
from bitarray import bitarray
import math
from libradsa import *

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

#CUDA packages
import pycuda.driver as cuda
import pycuda.autoinit
import pycuda.gpuarray as gpuarray
from pycuda.compiler import SourceModule
import pycuda.driver as drv
from pycuda import cumath
import numpy as np
import skcuda.linalg as linalg
import skcuda.misc as misc

import ctypes
# ctypes.CDLL('libgomp.so.1', mode=ctypes.RTLD_GLOBAL)
# ctypes.cdll.LoadLibrary('libcusolver.so')




def readdeco(filename,qbits):
    datastream = bitarray()
    if filename:
        with open(filename) as f:
            datastream.fromfile(f)
        
    ## Read data
    ## Should be improved
    chl0,chl1,chl2,chl3=demux(datastream)
    
    if qbits == 2:
        CH0,CH1,CH2,CH3=decode2bit(chl0,chl1,chl2,chl3)
    elif qbits == 4:
        CH0,CH1,CH2,CH3=decode4bit(chl0,chl1,chl2,chl3)
    elif qbits == 8:
        CH0,CH1,CH2,CH3=decode8bit(chl0,chl1,chl2,chl3)
    elif qbits == 16:
        CH0,CH1,CH2,CH3=decode16bit(chl0,chl1,chl2,chl3)    
    
    return CH0,CH1,CH2,CH3

# auxiliary function
def readdeco_aux(args):
    return readdeco(*args)

def main(args):
    
    lfile=[args.infileifms1, args.infileifms2, args.infileifms3]
    p = ThreadPool(3)
    job_args = [(lfile[i[0]],args.qbits) for i in enumerate(lfile)] 
    result = np.array(p.map(readdeco_aux, job_args))
    
    a = np.array([(result[0][0]).view(np.complex64).astype(np.complex128),
                  result[0][1].view(np.complex64).astype(np.complex128),
                  result[0][2].view(np.complex64).astype(np.complex128),
                  result[0][3].view(np.complex64).astype(np.complex128)])
    A=a.nbytes
    
    b = np.array([result[1][0].view(np.complex64).astype(np.complex128),
                  result[1][1].view(np.complex64).astype(np.complex128),
                  result[1][2].view(np.complex64).astype(np.complex128),
                  result[1][3].view(np.complex64).astype(np.complex128)])
    
    c = np.array([result[2][0].view(np.complex64).astype(np.complex128),
                  result[2][1].view(np.complex64).astype(np.complex128),
                  result[2][2].view(np.complex64).astype(np.complex128),
                  result[2][3].view(np.complex64).astype(np.complex128)])

    
    index=[(a[0].shape)[0],(b[0].shape)[0],(c[0].shape)[0]]
    
    drv.init()

    (free,total)=drv.mem_get_info()
    SIZE=int(free*25/100)
    nchunks=math.ceil(float(A)/SIZE)
    #print("25 of the memory:%f%% KB free"%((free*25/100)//1024))
    #print("Number of memory chunks: %d"%nchunks)

    ### We have to split the numpy array in chunks to fit the GPU Device memory
    linalg.init()
    step=int(math.ceil(a.shape[1]/nchunks))
    print step
    SUM=np.array([[ 0+0j ],[ 0+0j ],[ 0+0j ],[ 0+0j ]], dtype=np.complex128)
    
    gpu_sum = gpuarray.to_gpu(SUM)
    for i in range(0,int(a.shape[1]),step):
        aa=np.array([aux[(0+i):(i+step)] for aux in a])
        x_gpu = gpuarray.to_gpu(aa)
        (free,total)=drv.mem_get_info()
        #print("Global memory occupancy:%f%% free"%(free*100/total))
        y_gpu = linalg.conj(x_gpu)
        (free,total)=drv.mem_get_info()
        #print("Global memory occupancy:%f%% free"%(free*100/total))
        z_gpu = linalg.multiply(x_gpu, y_gpu)
        (free,total)=drv.mem_get_info()
        #print("Global memory occupancy:%f%% free"%(free*100/total))
        x_gpu.gpudata.free()
        y_gpu.gpudata.free()
        tmp_gpu=misc.sum(z_gpu,axis=1,keepdims=True)
        gpu_sum=gpu_sum+tmp_gpu
        tmp_gpu.gpudata.free()
        
    N = np.int32(index[0])
    RMS_gpu=cumath.sqrt(gpu_sum/N)
    (free,total)=drv.mem_get_info()
    RMS=RMS_gpu.get()
    gpu_sum.gpudata.free()
    RMS_gpu.gpudata.free()
    IFMS1=(",%f"*4)[1:] % tuple((RMS.real).flatten())
    
    gpu_sum = gpuarray.to_gpu(SUM)
    for i in range(0,int(a.shape[1]),step):
        bb=np.array([aux[(0+i):(i+step)] for aux in b])
        x_gpu = gpuarray.to_gpu(bb)
        (free,total)=drv.mem_get_info()
        y_gpu = linalg.conj(x_gpu)
        (free,total)=drv.mem_get_info()
        z_gpu = linalg.multiply(x_gpu, y_gpu)
        (free,total)=drv.mem_get_info()
        x_gpu.gpudata.free()
        y_gpu.gpudata.free()
        tmp_gpu=misc.sum(z_gpu,axis=1,keepdims=True)
        gpu_sum=gpu_sum+tmp_gpu
        tmp_gpu.gpudata.free()
        
    N = np.int32(index[1])
    RMS_gpu=cumath.sqrt(gpu_sum/N)
    (free,total)=drv.mem_get_info()
    RMS=RMS_gpu.get()
    gpu_sum.gpudata.free()
    RMS_gpu.gpudata.free()
    IFMS2=(",%f"*4)[1:] % tuple((RMS.real).flatten())
    
    gpu_sum = gpuarray.to_gpu(SUM)
    for i in range(0,int(c.shape[1]),step):
        cc=np.array([aux[(0+i):(i+step)] for aux in c])
        x_gpu = gpuarray.to_gpu(cc)
        (free,total)=drv.mem_get_info()
        y_gpu = linalg.conj(x_gpu)
        (free,total)=drv.mem_get_info()
        z_gpu = linalg.multiply(x_gpu, y_gpu)
        (free,total)=drv.mem_get_info()
        x_gpu.gpudata.free()
        y_gpu.gpudata.free()
        tmp_gpu=misc.sum(z_gpu,axis=1,keepdims=True)
        gpu_sum=gpu_sum+tmp_gpu
        tmp_gpu.gpudata.free()
        
    N = np.int32(index[2])
    RMS_gpu=cumath.sqrt(gpu_sum/N)
    (free,total)=drv.mem_get_info()
    RMS=RMS_gpu.get()
    gpu_sum.gpudata.free()
    RMS_gpu.gpudata.free()
    IFMS3=(",%f"*4)[1:] % tuple((RMS.real).flatten())
    
    string = os.path.basename(args.infileifms1)+','+IFMS1+','+\
             os.path.basename(args.infileifms2)+','+IFMS2+','+\
             os.path.basename(args.infileifms3)+','+IFMS3
    
    with open('result.txt', 'aw') as file:
        file.write(string)
        file.write("\n")

if __name__ == "__main__":
    
    import time
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Simulate antena data format.')
    parser.add_argument('-q', dest='qbits', type=int, choices=[2,4,8,16],
                        help="Bits quantization", required=True)
    parser.add_argument('-i1', '--infileifms1', dest='infileifms1',
                        help='Read from IN_FILE the simulated data.', required=True)
    parser.add_argument('-i2', '--infileifms2', dest='infileifms2',
                        help='Read from IN_FILE the simulated data.', required=True)
    parser.add_argument('-i3', '--infileifms3', dest='infileifms3',
                        help='Read from IN_FILE the simulated data.', required=True)
    
    args = parser.parse_args()
    
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))