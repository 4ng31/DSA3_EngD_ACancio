
# Antena Data Processor 
import numpy as np
import sys
import argparse
from bitarray import bitarray
from libradsa import *

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


def main(args):
    qbits=args.qbits
    
    datastream = bitarray()
    if args.infile:
        with args.infile as f:
            datastream.fromfile(f)
    
    ## Read data
    chl0,chl1,chl2,chl3=demux(datastream)
    
    if qbits == 1:
        decode1bit()
    elif qbits == 2:
        CH0,CH1,CH2,CH3=decode2bit(chl0,chl1,chl2,chl3)
    elif qbits == 4:
        CH0,CH1,CH2,CH3=decode4bit(chl0,chl1,chl2,chl3)
    elif qbits == 8:
        CH0,CH1,CH2,CH3=decode8bit(chl0,chl1,chl2,chl3)
    elif qbits == 16:
        CH0,CH1,CH2,CH3=decode16bit(chl0,chl1,chl2,chl3)
   



    a = np.array([CH0.view(np.complex64).astype(np.complex128),
         CH1.view(np.complex64).astype(np.complex128),
         CH2.view(np.complex64).astype(np.complex128),
         CH3.view(np.complex64).astype(np.complex128)])
    
    N = np.int32(a.shape[1])
    
    linalg.init()
    x_gpu = gpuarray.to_gpu(a)
    y_gpu = linalg.conj(x_gpu)
    z_gpu = linalg.multiply(x_gpu, y_gpu)
    x_gpu.gpudata.free()
    y_gpu.gpudata.free()
    RMS_gpu=cumath.sqrt(misc.sum(z_gpu,axis=1,keepdims=True)/N)
    RMS=RMS_gpu.get()
    RMS_gpu.gpudata.free()
   
    print args.infile.name,(RMS.real).flatten()
    
if __name__ == "__main__":

    import time
    start_time = time.time()
    parser = argparse.ArgumentParser(description='Simulate antena data format.')
    parser.add_argument('-q', dest='qbits', type=int, choices=[2,4,8,16],
                        help="Bits quantization", required=True)
    parser.add_argument('-i', '--infile', dest='infile',type=argparse.FileType('r'),
                        help='Read from IN_FILE the simulated data.', required=True)
    args = parser.parse_args()
    
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))