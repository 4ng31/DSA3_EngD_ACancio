
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

from pycuda.elementwise import ElementwiseKernel

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
    
    dt1=np.dtype(np.float32)
    dt2=np.dtype(np.complex64)
    
    a = np.array([result[0][0],result[0][1],result[0][2],result[0][3]])
    
    b = np.array([result[1][0],result[1][1],result[1][2],result[1][3]])
    
    c = np.array([result[2][0],result[2][1],result[2][2],result[2][3]])
    
    del result

    
    # define elementwise `square()` function
    square = ElementwiseKernel("float *a, float *b",
                               "b[i] = a[i]*a[i]",
                               "square")

    #Change data type of each element (bigger size)
    ## Maybe this has to be made in chunks
    a=a.astype(dt1)
    A=a.nbytes
      
    drv.init()
    (free,total)=drv.mem_get_info()
    SIZE=int(free*20/100)
    nchunks=math.ceil(float(A)/SIZE)

    ### We have to split the numpy array in chunks to fit the GPU Device memory
    misc.init()
    
    step=int(math.ceil(a.shape[1]/nchunks))
    start_t = time.time()
    gpu_sum = gpuarray.to_gpu(np.array([[ 0. ],[ 0. ],[ 0. ],[ 0. ]], dtype=dt1))
    for i in range(0,int(a.shape[1]),step):
        x_gpu = gpuarray.to_gpu(a[0::,0+i:i+step])
        y_gpu = gpuarray.empty_like(x_gpu)
        square(x_gpu, y_gpu)
        tmp_gpu=misc.sum(y_gpu,axis=1,keepdims=True)
        gpu_sum=gpu_sum+tmp_gpu
    N = np.int32((a[0].shape)[0])
    summ=gpu_sum.get()
    RMS=np.sqrt(summ.real/N)
    IFMS1=(",%f"*4)[1:] % tuple((RMS.real).flatten())
    gpu_sum.gpudata.free()
    print("--- %s seconds ---" % (time.time() - start_t))
    del a

    b=b.astype(dt1)
    B=b.nbytes
      
    drv.init()
    (free,total)=drv.mem_get_info()
    SIZE=int(free*20/100)
    nchunks=math.ceil(float(B)/SIZE)

    ### We have to split the numpy array in chunks to fit the GPU Device memory
    misc.init()
    
    step=int(math.ceil(b.shape[1]/nchunks))
    start_t = time.time()
    gpu_sum = gpuarray.to_gpu(np.array([[ 0. ],[ 0. ],[ 0. ],[ 0. ]], dtype=dt1))
    for i in range(0,int(b.shape[1]),step):
        x_gpu = gpuarray.to_gpu(b[0::,0+i:i+step])
        y_gpu = gpuarray.empty_like(x_gpu)
        square(x_gpu, y_gpu)
        tmp_gpu=misc.sum(y_gpu,axis=1,keepdims=True)
        gpu_sum=gpu_sum+tmp_gpu
    N = np.int32((b[0].shape)[0])
    summ=gpu_sum.get()
    RMS=np.sqrt(summ.real/N)
    IFMS2=(",%f"*4)[1:] % tuple((RMS.real).flatten())
    gpu_sum.gpudata.free()
    print("--- %s seconds ---" % (time.time() - start_t))
    del b

    
    c=c.astype(dt1)
    C=c.nbytes
      
    drv.init()
    (free,total)=drv.mem_get_info()
    SIZE=int(free*20/100)
    nchunks=math.ceil(float(C)/SIZE)

    ### We have to split the numpy array in chunks to fit the GPU Device memory
    misc.init()
    
    step=int(math.ceil(c.shape[1]/nchunks))
    start_t = time.time()
    gpu_sum = gpuarray.to_gpu(np.array([[ 0. ],[ 0. ],[ 0. ],[ 0. ]], dtype=dt1))
    for i in range(0,int(c.shape[1]),step):
        x_gpu = gpuarray.to_gpu(c[0::,0+i:i+step])
        y_gpu = gpuarray.empty_like(x_gpu)
        square(x_gpu, y_gpu)
        tmp_gpu=misc.sum(y_gpu,axis=1,keepdims=True)
        gpu_sum=gpu_sum+tmp_gpu
    N = np.int32((c[0].shape)[0])
    summ=gpu_sum.get()
    RMS=np.sqrt(summ.real/N)
    IFMS3=(",%f"*4)[1:] % tuple((RMS.real).flatten())
    gpu_sum.gpudata.free()
    print("--- %s seconds ---" % (time.time() - start_t))
    del c

    string = os.path.basename(args.infileifms1)+','+IFMS1+','+\
             os.path.basename(args.infileifms2)+','+IFMS2+','+\
             os.path.basename(args.infileifms3)+','+IFMS3
    
    with open(args.out, 'aw') as file:
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
    parser.add_argument('-o', '--out', dest='out',
                        help='Output file where store the result.', required=True)
    
    args = parser.parse_args()
    
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))