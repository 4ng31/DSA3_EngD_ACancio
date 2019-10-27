
# Antena Data format simulator 
import numpy as np
import sys
import argparse

from bitarray import bitarray
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial

from libradsa import * 

def roundup(nsamples,qbits):
    """Round number of bits for IQ data fill a byte (nearest multiple)
    
    Notes
    =====
    @param nsamples : number of pairs IQ
           qbits : data quantization bits, allowed 2, 4, 8, 16
    """
    n = nsamples*qbits
    m = 8
    a=((n + m - 1) / m) * m 
    return a

def channel(qbits,npairs):
    """Generate IQ bits data
    
    Notes
    =====
    @param qbits :  data quantization bits, allowed 2, 4, 8, 16
           npairs : Number of pairs IQ
    """
    if qbits in [2, 4, 8, 16]:
        nsamples = npairs
        maxim=(2**(qbits-1))
        minim=-1*(2**(qbits-1))
        
        bitsamples = roundup(nsamples,qbits)
        nsamples = bitsamples/qbits
        
        IQ=np.random.randint(minim,maxim,nsamples,dtype='int16')
        aux=IQ.view(dtype='uint16')
        del IQ
        d=[('0000000000000000'+bin(xi)[2:])[-qbits:] for xi in aux]
        del aux
        a=bitarray(''.join(d))
        del d
    else:
        raise TypeError('Please set quantization bits to 2,4,8 or 16')
        
    return a   

def main(args):
    qbits=args.qbits
    npairs=args.nsamples*2
    
    if args.test:
        npairs=4*2
    
    #If npair > 1e6 chunck
    N=int(npairs/1e6)
    R=int(npairs%1e6)
    
    print "Number of chunks",N
    print "Last chunk",R
    
    
    for i in range(0, N):
        ## Create data
        pool = ThreadPool(4) 
        iterable = [ int(1e6), int(1e6), int(1e6), int(1e6)]
        func = partial(channel, qbits)
        result = pool.map(func, iterable)
        datastream=mux(result[0],result[1],result[2],result[3])
        del result
        print 'datastream length',datastream.length()
        if args.outfile:
            with open(args.outfile, 'a') as f:
                datastream.tofile(f)
                
    
    ## Create data
    pool = ThreadPool(4) 
    iterable = [ R, R, R, R]
    func = partial(channel, qbits)
    result = pool.map(func, iterable)
    datastream=mux(result[0],result[1],result[2],result[3])
    del result
    print 'datastream length',datastream.length()
    if args.outfile:
        with open(args.outfile, 'a') as f:
            datastream.tofile(f)
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Simulate antena data format.')
    parser.add_argument('-q', dest='qbits', type=int, choices=[2,4,8,16],
                        help="Bits quantization", required=True)
    parser.add_argument('-n', dest='nsamples', type=int,
                        help='Numdeb of IQ pairs (samples*2)', required=True)
    parser.add_argument('-o', '--outfile', dest='outfile',type=str,
                        help='Write to OUT_FILE the simulated data.', required=True)
    parser.add_argument('-t', '--test', dest='test',type=str,
                        help='Print 4 samples pairs', required=False)
    
    args = parser.parse_args()
    
    main(args)