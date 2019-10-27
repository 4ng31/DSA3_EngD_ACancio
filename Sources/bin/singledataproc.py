
# Antena Data Processor 
import numpy as np
import sys,os
import argparse
from bitarray import bitarray
import math
from libradsa import *

import multiprocessing
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

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

def main(args):
    
    result = np.array(readdeco(args.infileifms, args.qbits))
#     print result
    dt1=np.dtype(np.float32)
    dt2=np.dtype(np.complex64)
    
    
    a = np.array([result[0],
                  result[1],
                  result[2],
                  result[3]])
   
    del result
    
    a=a.astype(dt1)
    
    ##Mapping    
    if args.qbits == 2:
        a=16384*a+8192
    elif args.qbits == 4:
        a=4096*a+2048
    elif args.qbits == 8:
        a=256*a+128
    elif args.qbits == 16:
        a=a+0.5
    
    a=a.view(dt2)
#     print a.shape
#     print a.nbytes
    ### We have to split the numpy array in chunks to fit size similar to the GPU Device
    A=a.nbytes
    SIZE=2147483648 #2048 MBytes
    nchunks=math.ceil(float(A)/SIZE)
    
    step=int(math.ceil(a.shape[1]/nchunks))
    SUM=np.array([ 0.+0.j , 0.+0.j , 0.+0.j , 0+0.j ], dtype=dt2)
    print SUM.shape
    for i in range(0,int(a.shape[1]),step):
        x = np.array(a[0::,0+i:i+step])
        y=np.conjugate(x)
        z=np.multiply(x,y)
        del x
        del y
        thesum=np.sum(z, axis=1)
        SUM=np.add(SUM,thesum)
        del z
        
    N = np.int32((a[0].shape)[0])
    RMS=np.sqrt(SUM.real/N)
    IFMS=(",%f"*4)[1:] % tuple((RMS).flatten())
    del RMS
    del a
    
    string = os.path.basename(args.infileifms)+','+IFMS    
    print string
    
    with open(args.outfile, 'aw') as file:
        file.write(string)
        file.write("\n")

if __name__ == "__main__":
    
    import time
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Simulate antena data format.')
    parser.add_argument('-q', dest='qbits', type=int, choices=[2,4,8,16],
                        help="Bits quantization", required=True)
    parser.add_argument('-i', '--infileifms', dest='infileifms',
                        help='Read from IN_FILE the simulated data.', required=True)
    parser.add_argument('-o', '--outfile', dest='outfile',
                        help='Write to OUT_FILE', required=True)
    
    args = parser.parse_args()
    
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))