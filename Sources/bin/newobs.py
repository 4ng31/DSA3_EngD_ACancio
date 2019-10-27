#!/usr/bin/python
# -*- coding: utf-8 -*-
#"""
#@author: Angel Cancio
#"""

import os
import sys
import argparse
import binascii
import numpy as np
from bitarray import bitarray
from math import log10
from astropy.table import Table, Column
from astropy.io import ascii

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
        print yaml.dump(header, default_flow_style=False)
        
    return header

def readdatabytes(filename):
    """
    Notes
    =====
    
    """
    
    fsize=os.path.getsize(filename)
    datasize=(fsize/1468)*1392 ## BYTES
    
    #print 'File Size',fsize
    #print 'Data Size',datasize
    
    fh = bitarray()  
    da = bitarray(datasize*8) ### BITS
    da.setall(False)
    
    with open(filename, 'rb') as f:
        fh.fromfile(f)
    
    j=0
    i=0
    
#     # For 8 bits
#     bits=8*1468 # Block bytes to bits
#     SFrame=174  # Samples per frame
#     auxgain=np.ones(SFrame)
    
    # For 16 bits
    bits=8*1468 # Block bytes to bits
    SFrame=87 # Samples per frame
    auxgain=np.ones(SFrame)
    
    a=np.arange(0,SFrame,1)
    secondarray = np.zeros(SFrame*(fsize/1468))
    gain_cfe = np.zeros(SFrame*(fsize/1468))
    gain_digital = np.zeros(SFrame*(fsize/1468))

    flag=0
    gainchek1=-99
    gainchek2=-99
    while True:
        header = bitarray()
        data = bitarray()    

        aux=bits*i
        aux1=aux+8*76
        aux2=aux+bits
        
        header = fh[aux:aux1]    
        hd = readheader(header.tobytes(),hprint=False)
        SR=np.float64((17.5e6)/(hd["samplerate"]))
        PERIOD = np.float(1.000000/SR)
        
        
        if gainchek1==-99:
            gainchek1=hd["cfegain"]
        
        if not gainchek1==hd["cfegain"]:
            print "CFE Gain Not Fixed"
        
        if gainchek2==-99:
            gainchek2=hd["digitalgain"]
        
        if not gainchek2==hd["digitalgain"]:
            print "Digital Gain Not Fixed"
        
        #print SR
        #print PERIOD
        
        start=np.float64(hd["timetag_secs"]+hd["timetag_samps"]*1./17.5e6-hd["path_delay"]*1./35e6)
        end=start+SFrame*PERIOD     
        
        if flag == 0:
            time1=sec2time(start, n_msec=3)
            #print 'Start Time',time #,'End Time', end,'PERIOD',PERIOD,'SFrame', SFrame
            flag = 99
        
#         timearray=np.arange(start,end,PERIOD)
        timearray2=np.linspace(start,end,num=87,retstep=True)
        timearray=timearray2[0]
        #print 'Period Error', PERIOD-timearray2[1]
           
        subchan0_offset=(hd["subchan0_offset"]*35e6)/2**32
        subchan1_offset=(hd["subchan1_offset"]*35e6)/2**32
        subchan2_offset=(hd["subchan2_offset"]*35e6)/2**32
        subchan3_offset=(hd["subchan3_offset"]*35e6)/2**32
        
        #print subchan0_offset,subchan1_offset,subchan2_offset,subchan3_offset
        
#         if not flag == 0:
#             acum=0
#             for element in timearray:
#                 print acum,element
#                 acum+=1
#             sys.exit(1)    
#         flag=1
#         print "Start time", start
#         print len(timearray)
#         print len(secondarray)
        secondarray[i*SFrame:(i+1)*SFrame]=timearray
        
        gain_cfe[i*SFrame:(i+1)*SFrame]=auxgain*hd["cfegain"]
        
        gain_digital[i*SFrame:(i+1)*SFrame]=auxgain*hd["digitalgain"]
        
        data = fh[aux1:aux2]
        
        i=i+1
        
        jold=j
        j=j+data.length()
        da[jold:jold+data.length()]=data    
        
        if aux2 == len(fh):
            #print 'Start Time',start,
            time2=sec2time(end, n_msec=3)
            print filename, time1, time2
            break
            
#         acum=0
#         for element in timearray:
#             print acum,element
#             acum+=1
        
        del timearray
    
#     print i
#     print len(secondarray)
    return da,secondarray,gain_cfe,gain_digital,i

def demux(stream):
    """Demultiplex data and separate channels
    
    Notes
    =====
    @param stream : bitarray of multiplexed bits channels
    """
    
    b=bitarray(stream.length()/2)
    c=bitarray(stream.length()/2)
    b.setall(False)
    c.setall(False)
    
    ch0 = bitarray(stream.length())
    ch1 = bitarray(stream.length())
    ch2 = bitarray(stream.length())
    ch3 = bitarray(stream.length())
    ch0.setall(False)
    ch1.setall(False)
    ch2.setall(False)
    ch3.setall(False)

    b, c = stream[::2], stream[1::2]
    ch0, ch2 = b[::2], b[1::2]
    ch1, ch3 = c[::2], c[1::2]

    return ch0,ch1,ch2,ch3


def pow_to_dB(mW):
    """This function converts a power given in mW to a power given in dBm."""
    return 10.*np.log10(mW)

def dbm_to_mw(dBm):
    """This function converts a power given in dBm to a power given in mW."""
    return 10**((dBm)/10.)

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

def time2sec(time, n_msec=3):
    ''' Convert 'D days, HH:MM:SS.FFF' to seconds'''
    from datetime import datetime as dt
    pt=dt.strptime(time,'%H:%M:%S.%f')
    total_seconds=pt.second+pt.minute*60+pt.hour*3600
    return total_seconds


def process(thefile):
    #print 'Testing'

    # filename='/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0001'
    
    root,filename=os.path.split(thefile)
    outputfile='/home/taller-dis1/Angel/'+filename+'_ASCII.dat'
    print root
    print outputfile

    
    try:
        os.remove(outputfile)
        #print("Files Removed!")
    except:
        count=1
        #print "No files to delete"

    print filename
    # readdatabytes(filename)
    data,time,gaincfe,gaindigital,nblocks=readdatabytes(root+'/'+filename)

#     if len(gaincfe) == nblocks:
#         print "OK",nblocks
    
    ch0,ch1,ch2,ch3 = demux(data)

    # 8 bits are  8-bit complex samples--i.e. 4 bits and 4 bits for imaginary and real (Q and I) 
    # dt = np.dtype(np.int8)
    # dt = dt.newbyteorder('>')

    dt = np.dtype(np.int16)
    dt = dt.newbyteorder('>')
    
    # CH0,CH1,CH2,CH3 = (np.zeros(len(ch0)/32) for _ in xrange(4))
    # CH0=np.frombuffer(ch0, dtype=np.int8)
    # CH1=np.frombuffer(ch1, dtype=np.int8)
    # CH2=np.frombuffer(ch2, dtype=np.int8)
    # CH3=np.frombuffer(ch3, dtype=np.int8)

    CH0=(np.frombuffer(ch0, dtype=dt))+.5
    CH1=(np.frombuffer(ch1, dtype=dt))+.5
    CH2=(np.frombuffer(ch2, dtype=dt))+.5
    CH3=(np.frombuffer(ch3, dtype=dt))+.5

    CH0I=CH0[::2]
    CH0Q=CH0[1::2]
    CH1I=CH1[::2]
    CH1Q=CH1[1::2]
    CH2I=CH2[::2]
    CH2Q=CH2[1::2]
    CH3I=CH3[::2]
    CH3Q=CH3[1::2]

    # CH0I = np.bitwise_and(CH0, 0xf0).astype(np.int8) >> 4
    # CH0Q=(np.bitwise_and(CH0, 0x0f) << 4).astype(np.int8) >> 4
    # CH1I = np.bitwise_and(CH1, 0xf0).astype(np.int8) >> 4
    # CH1Q=(np.bitwise_and(CH1, 0x0f) << 4).astype(np.int8) >> 4
    # CH2I = np.bitwise_and(CH2, 0xf0).astype(np.int8) >> 4
    # CH2Q=(np.bitwise_and(CH2, 0x0f) << 4).astype(np.int8) >> 4
    # CH3I = np.bitwise_and(CH3, 0xf0).astype(np.int8) >> 4
    # CH3Q=(np.bitwise_and(CH3, 0x0f) << 4).astype(np.int8) >> 4

    # #Mapping 4096m+2048
    # CH0Im=4096*CH0I+2048
    # CH0Qm=4096*CH0Q+2048
    # CH1Im=4096*CH1I+2048
    # CH1Qm=4096*CH1Q+2048
    # CH2Im=4096*CH2I+2048
    # CH2Qm=4096*CH2Q+2048
    # CH3Im=4096*CH3I+2048
    # CH3Qm=4096*CH3Q+2048


    #print len(time),len(CH0I),len(CH0Q),len(CH0I),len(CH1Q),len(CH2I),len(CH2Q),len(CH3I),len(CH3Q)
    with open(outputfile,'a') as ff:
        np.savetxt(ff, np.c_[time, CH0I,CH0Q, CH1I,CH1Q, CH2I,CH2Q, CH3I,CH3Q])

    #print "Done!"

    
def main(args):
#     print args.filename
    
    if args.filename:
        process(args.filename)
    
    return 0
    
if __name__ == '__main__':
      
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-f', '--filename', help='File to process', default='False')
    
    args = parser.parse_args()
   
    main(args)