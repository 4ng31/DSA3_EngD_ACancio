import argparse
import os,sys
import mmap
import struct
import numpy as np
from bitstring import BitStream, ConstBitStream,Bits
from bitstring import BitArray as bt
from bitarray import bitarray as BitArray

def readheader(BS,hprint=None):
    b = BitStream('0x'+''.join(x.encode('hex') for x in struct.unpack('>76s',BS)))
    magic = b.read(32).hex# 32 magic word
    header = {}
    header["recordlength"] = b.read(16).uint   # 16 0..65535
    header["hdrlen"] = b.read(8).uint    # 8 0..255
    header["blocksize"] = b.read(8).uint   # 8 0..25
    header["samplerate"] = b.read(16).uint   # 16 0..65535
    header["efegain"] = b.read(10).uint   # 10 0..650
    header["qu"] = b.read(3).uint    # 16 0..7 (0=>1bits,1=>2bits,2=>4bits,4=>8bits,5=>16bits, 3,6,7 spare)
    header["msg"] = b.read(3).uint    # 3 6
    header["frameid"] = b.read(32).uint  # 32 0..4294967295
    header["version"] = b.read(7).uint    # 7 0..127
    header["timetag_samps"] = b.read(25).uint   # 25 0..17499999
    header["offsetfreq"] = b.read(32).int   # 32 0..4294967295
    header["timetag_secs"] = b.read(17).uint   # 17 0..86399
    header["subc"] = b.read(4).uint    # 4 0..16
    header["digitalgain"] = b.read(11).uint   # 11 0..2047
    header["subchan0_offset"] = b.read(32).int    # 32 -2147483647..+2147483647
    header["subchan1_offset"] = b.read(32).int    # 32 -2147483647..+2147483647
    header["subchan2_offset"] = b.read(32).int    # 32 -2147483647..+2147483647
    header["subchan3_offset"] = b.read(32).int    # 32 -2147483647..+2147483647
    header["sweeprate"] = b.read(32).int    # 32 -2147483647..+2147483647
    header["path_delay"] = b.read(32).int    # 32 0..2^32-1
    header["gdspid"] = b.read(8).uint    # 1 0..1
    header["hs"] = b.read(1).uint    # 1 0..1
    header["semr"] = b.read(12).int    # 12
    header["sweepchange"] = b.read(11).uint   # 11 0..2047
    header["ncov"] = b.read(1).uint    # 1 0..1
    header["ncoreset_c"] = b.read(11).int    # 11 -1024..+1024
    header["ncoreset_t"] = b.read(20).uint   # 20 0..863999
    b.read(128).uint    # 128 Empty
    
    if hprint:
        #print header
        print yaml.dump(header, default_flow_style=False)
    
    return header

def bymmap(INFILE):
    SIZE = os.stat(INFILE).st_size
    print SIZE
    BYTES=1468
    SKIP=76
    
    print('RFCH0,RFCH1,RFCH2,RFCH3')
    with open(INFILE, 'rb') as fd:
        mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
        for offset in range(0, SIZE, BYTES):
#             print offset, offset+SKIP
            # Read Header (check cuantization and save timestamp)
            header = readheader(mm[offset:offset+SKIP],hprint=False)
#             print header["efegain"],header["digitalgain"]
            time=hd["timetag_secs"]+hd["timetag_samps"]*1./17.5e6-hd["path_delay"]*1./35e6
            
            FreqDnlkConv = 8379400000  # Hz
            EolpSubC0FreqOffs  = -100000  # Hz
            EolpSubC1FreqOffs  = 0  # Hz
            EolpSubC2FreqOffs  = 100000  # Hz
            EolpSubC3FreqOffs  = 200000  # Hz
            aux=70e5+FreqDnlkConv
            conv=35e6/2**32
            RF0 = +header["offsetfreq"]*conv+header["subchan0_offset"]*conv-EolpSubC0FreqOffs
            RF1 = +header["offsetfreq"]*conv+header["subchan0_offset"]*conv-EolpSubC1FreqOffs
            RF2 = +header["offsetfreq"]*conv+header["subchan0_offset"]*conv-EolpSubC2FreqOffs
            RF3 = +header["offsetfreq"]*conv+header["subchan0_offset"]*conv-EolpSubC3FreqOffs
            print('RF: %f,%f,%f,%f'%(RF0,RF1,RF2,RF3))
            
    print 'Done'
             

def main(args):
    bymmap(args.infile)
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extract binary data, remove UDP headers')
    parser.add_argument('-i','--infile', dest='infile', help='Path of a file', required=True)
    args = parser.parse_args()
    
    main(args)