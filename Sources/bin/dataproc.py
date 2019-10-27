
# Antena Data Processor 
import numpy as np
import sys
import argparse
from bitarray import bitarray
from libradsa import *

#CUDA packages
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule


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

#     print CH0
#     print CH1
#     print CH2
#     print CH3
    
    # a = numpy.random.randn(4,2)
# a = a.astype(numpy.float32)
# a_gpu = cuda.mem_alloc(a.size * a.dtype.itemsize)

# cuda.memcpy_htod(a_gpu, a)

# mod = SourceModule("""
#     __global__ void doublify(float *a)
#     {
#       int idx = threadIdx.x + threadIdx.y*4;
#       a[idx] *= 2;
#     }
#     """)

# func = mod.get_function("doublify")
# func(a_gpu, block=(4,4,1))

# a_doubled = numpy.empty_like(a)
# cuda.memcpy_dtoh(a_doubled, a_gpu)
# print "original array:"
# print a
# print "doubled with kernel:"
# print a_doubled
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simulate antena data format.')
    parser.add_argument('-q', dest='qbits', type=int, choices=[2,4,8,16],
                        help="Bits quantization", required=True)
    parser.add_argument('-i', '--infile', dest='infile',type=argparse.FileType('r'),
                        help='Read from IN_FILE the simulated data.', required=True)
    args = parser.parse_args()
    
    main(args)