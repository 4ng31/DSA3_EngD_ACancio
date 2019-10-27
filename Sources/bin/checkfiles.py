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

def sec2time(sec, n_msec=3):
    ''' Convert seconds to 'D days, HH:MM:SS.FFF' '''
    if hasattr(sec,'__len__'):
        return [sec2time(s) for s in sec]
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if n_msec > 0:
        pattern = '%%02d:%%02d:%%0%d.%df' % (n_msec+3, n_msec)
    else:
        pattern = r'%02d:%02d:%02d'
    if d == 0:
        return pattern % (h, m, s)
    return ('%d days, ' + pattern) % (d, h, m, s)


def readblock(filepointer, startbyte,endbyte):
    a = bt(filepointer)
    H=76*8
    R=1392*8
    pkg=H+R
    print a.len
    for i in range(0,a.len/pkg):
        del a[i*(R):i*(R)+H]
    print a.len

def check(INFILE):
    SIZE = os.stat(INFILE).st_size
    print SIZE
    BYTES=1468
    HEADER=76
    
    with open(INFILE, 'rb') as fd:
        mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
        BS= mm[0:HEADER]
        header1 = readheader(BS,hprint=None)
        X=np.float64(header1["timetag_samps"])*np.float64(1./17500000)
        Y=np.float64(header1["path_delay"])*np.float64(1./35000000)
        utctime=np.float64(header1["timetag_secs"])+X-Y
        ttime1=sec2time(utctime,6)
        BS = mm[SIZE-BYTES:SIZE-BYTES+HEADER]
        header2 = readheader(BS,hprint=None)
        X=np.float64(header2["timetag_samps"])*np.float64(1./17500000)
        Y=np.float64(header2["path_delay"])*np.float64(1./35000000)
        utctime=np.float64(header2["timetag_secs"])+X-Y
        ttime2=sec2time(utctime,6)

    print INFILE,ttime1,ttime2
            
def main(args):
    check(args.infile)
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Check binary data')
    parser.add_argument('-i','--infile', dest='infile', help='Path of a file', required=True)
#     parser.add_argument('-o','--outfile', dest='outfile', help='Path of a file', required=True)
    args = parser.parse_args()
    
    main(args)