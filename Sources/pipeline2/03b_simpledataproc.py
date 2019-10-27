
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
    
    a = np.array([result[0][0],
                  result[0][1],
                  result[0][2],
                  result[0][3]])
   
    b = np.array([result[1][0],
                  result[1][1],
                  result[1][2],
                  result[1][3]])
    
    c = np.array([result[2][0],
                  result[2][1],
                  result[2][2],
                  result[2][3]])
    del result
    
    a=a.astype(dt1).view(dt2)
    ### We have to split the numpy array in chunks to fit size similar to the GPU Device
    A=a.nbytes
    SIZE=2147483648 #2048 MBytes
    nchunks=math.ceil(float(A)/SIZE)
    
    step=int(math.ceil(a.shape[1]/nchunks))
    SUM=np.array([ 0.+0.j , 0.+0.j , 0.+0.j , 0+0.j ], dtype=dt2)
    
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
    IFMS1=(",%f"*4)[1:] % tuple((RMS).flatten())
    del RMS
    del a
    
    b=b.astype(dt1).view(dt2)
    B=b.nbytes
    nchunks=math.ceil(float(B)/SIZE)
    step=int(math.ceil(c.shape[1]/nchunks))
    SUM=np.array([ 0.+0.j , 0.+0.j , 0.+0.j , 0+0.j ], dtype=dt2)
    
    for i in range(0,int(b.shape[1]),step):
        x = np.array(b[0::,0+i:i+step])
        y=np.conjugate(x)
        z=np.multiply(x,y)
        del x
        del y
        thesum=np.sum(z, axis=1)
        SUM=np.add(SUM,thesum)
        del z
        
    N = np.int32((b[0].shape)[0])
    RMS=np.sqrt(SUM.real/N)
    IFMS2=(",%f"*4)[1:] % tuple((RMS).flatten())
    del RMS
    del b
    
    c=c.astype(dt1).view(dt2)
    C=c.nbytes
    nchunks=math.ceil(float(C)/SIZE)
    step=int(math.ceil(c.shape[1]/nchunks))
    SUM=np.array([ 0.+0.j , 0.+0.j , 0.+0.j , 0+0.j ], dtype=dt2)
    
    for i in range(0,int(c.shape[1]),step):
        x = np.array(c[0::,0+i:i+step])
        y=np.conjugate(x)
        z=np.multiply(x,y)
        del x
        del y
        thesum=np.sum(z, axis=1)
        SUM=np.add(SUM,thesum)
        del z
        
    N = np.int32((c[0].shape)[0])
    RMS=np.sqrt(SUM.real/N)
    IFMS3=(",%f"*4)[1:] % tuple((RMS).flatten())
    del RMS
    del c
    
    string = os.path.basename(args.infileifms1)+','+IFMS1+','+\
             os.path.basename(args.infileifms2)+','+IFMS2+','+\
             os.path.basename(args.infileifms3)+','+IFMS3
    
    print string
    
    with open('result_simple.txt', 'aw') as file:
        file.write(string)
        file.write("\n")

if __name__ == "__main__":
    
    import time
    start_time = time.time()
    
    parser = argparse.ArgumentParser(description='Simulate antena data format.')
    parser.add_argument('-q', dest='qbits', type=int, choices=[2,4,8,16],
                        help="Bits quantization", required=True)
    parser.add_argument('-i1', '--infileifms1', dest='infileifms1',
                        help='Read from IN_FILE the simulated data.', required=False)
    parser.add_argument('-i2', '--infileifms2', dest='infileifms2',
                        help='Read from IN_FILE the simulated data.', required=False)
    parser.add_argument('-i3', '--infileifms3', dest='infileifms3',
                        help='Read from IN_FILE the simulated data.', required=False)
    
    args = parser.parse_args()
    
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))