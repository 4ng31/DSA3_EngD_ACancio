# -*- coding: utf-8 -*-
import os
import struct
import mmap
import sys
import yaml
import argparse
import multiprocessing
import numpy as np
from bitstring import BitStream, ConstBitStream,Bits
from bitstring import BitArray as bt
from bitarray import bitarray as BitArray
from itertools import chain
import csv

def readheader(BS,hprint=None):
    """Reads the header of a UNIX format raw data file.
    Notes
    =====
    @param BS : byte stream
    """
    
    from bitstruct import unpack
    
    header={}
    header["magic"],header["recordlength"],header["hdrlen"],header["blocksize"],\
    header["samplerate"],header["cfegain"],header["qu"],header["msg"],\
    header["frameid"],header["version"],header["timetag_samps"],header["offsetfreq"],\
    header["timetag_secs"],header["subc"],header["digitalgain"],header["subchan0_offset"],\
    header["subchan1_offset"],header["subchan2_offset"],header["subchan3_offset"],\
    header["sweeprate"],header["path_delay"],header["gdspid"],header["hs"],\
    header["semr"],header["sweepchange"],header["ncov"],header["ncoreset_c"],\
    header["ncoreset_t"],empty = unpack('>r32u16u8u8u16u10u3u3u32u7u25s32u17u4u11s32s32s32s32s32s32u8u1s12u11u1s11u20r128', BS)
                  
    if hprint:
        import yaml
        print(yaml.dump(header, default_flow_style=False))
        
    return header

def readblock(filepointer, startbyte,endbyte):
    a = bt(filepointer)
    H=76*8
    R=1392*8
    pkg=H+R
    print a.len
    for i in range(0,a.len/pkg):
        del a[i*(R):i*(R)+H]
    print a.len

def bymmap(INFILE,OUTFILE):
    SIZE = os.stat(INFILE).st_size
    print SIZE
    BYTES=1468
    SKIP=76
    
    with open(INFILE, 'rb') as fd:
        mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
        for offset in range(0, SIZE, BYTES):
            data = mm[offset+SKIP:offset+BYTES]
            with open(OUTFILE, 'ab') as f:
                f.write(data)
    print 'Done'
    
            
def main(args):
    bymmap(args.infile,args.outfile)
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract binary data, remove UDP headers')
    parser.add_argument('-i','--infile', dest='infile', help='Path of a file', required=True)
    parser.add_argument('-o','--outfile', dest='outfile', help='Path of a file', required=True)
    args = parser.parse_args()
    
    main(args)