
## Test gain correction
## 72009.9946645,20:00:09.994665,176.0,/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0004,0,77190376
import os
# import glob
# import datetime
# import mmap
import sys
# import gc
import numpy as np
from bitarray import bitarray
from math import log10
from astropy.table import Table, Column
from astropy.io import ascii

# import talib as ta

#from skrf import mathFunctions

# import timeit

print 'Testing'

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

def createheader(filename,timetag_sec,timetag_samp,delay,deltaID,frequency,quantization,muxflag):
    """
    Notes
    =====
    
    """
    
    
    import struct
    codename = struct.pack('>4s', 'AACM') # 
    sTimetag_sec = struct.pack('>I', timetag_sec) #
    sTimetag_samp= struct.pack('>I', timetag_samp) #
    sDelay = struct.pack('>I', delay) #
    sDeltaID = struct.pack('>I', deltaID) #
    sFrequency = struct.pack('>I', frequency) #
    sQuantization = struct.pack('>I', quantization) #
    sMuxflag = struct.pack('>H', muxflag) #
    
    string = codename+sTimetag_sec+sTimetag_samp+sDelay+sFrequency+sDeltaID+sQuantization+sMuxflag
    with open(filename+'final.bin', 'wb') as f:
        f.write(string)

def readdatabytes(filename):
    """
    Notes
    =====
    
    """
    
    fsize=os.path.getsize(filename)
    datasize=(fsize/1468)*1392 ## BYTES
    
    fh = bitarray()  
    da = bitarray(datasize*8) ### BITS
    da.setall(False)
    
    with open(filename, 'rb') as f:
        fh.fromfile(f)
    
    j=0
    i=0
    bits=8*1468
    auxgain=np.ones(87)
    
    a=np.arange(0,87,1)
    secondarray = np.zeros(87*(fsize/1468))
    gain_cfe = np.zeros(87*(fsize/1468))
    gain_digital = np.zeros(87*(fsize/1468))
    SR=int((17.5e6)/(176))
    PERIOD = 1./SR
    
    while True:
        header = bitarray()
        data = bitarray()    

        aux=bits*i
        aux1=aux+8*76
        aux2=aux+bits
        
        header = fh[aux:aux1]    
        hd = readheader(header.tobytes(),hprint=False)
        
        start=hd["timetag_secs"]+hd["timetag_samps"]*1./17.5e6-hd["path_delay"]*1./35e6

        timearray=a*PERIOD+start

#         timearray=np.arange(start,start+87*PERIOD,PERIOD)
        
        secondarray[i*87:(i+1)*87]=timearray
        2
        gain_cfe[i*87:(i+1)*87]=auxgain*hd["cfegain"]
        
        gain_digital[i*87:(i+1)*87]=auxgain*hd["digitalgain"]
        
        data = fh[aux1:aux2]
        
        i=i+1
        
        jold=j
        j=j+data.length()
        da[jold:jold+data.length()]=data    
        
        if aux2 == len(fh):
            break
            
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


def mw_to_dbm(mW):
    """This function converts a power given in mW to a power given in dBm."""
    return 10.*np.log10(mW)

def dbm_to_mw(dBm):
    """This function converts a power given in dBm to a power given in mW."""
    return 10**((dBm)/10.)

def time2sec(time, n_msec=3):
    ''' Convert 'D days, HH:MM:SS.FFF' to seconds'''
    from datetime import datetime as dt
    pt=dt.strptime(time,'%H:%M:%S.%f')
    total_seconds=pt.second+pt.minute*60+pt.hour*3600
    return total_seconds


# ## Source 1934-638
# ll = ['ON - PSK 1934-638',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0001',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0003',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0003',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0001',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0003',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0003',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0006',
#       'OFF',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0009',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0009',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0004',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0009',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0009',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0004',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0009',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0009',
#       'ON - QSO B0521-365',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0010',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0016',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0029',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0004',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0010',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0016',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0029',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0004',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0010',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0016',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0029',
#       'OFF',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0007',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0013',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0019',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_195710_0032',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0007',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0013',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0019',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_195714_0032',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0007',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0013',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0019',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_195718_0032',
#       'ON - QSO B1145-676',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0009',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0018',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0024',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0003',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0009',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0018',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0024',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0003',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0009',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0018',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0024',
#       'OFF',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0012',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0021',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_205821_0027',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0012',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0021',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_205825_0027',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0012',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0021',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_205829_0027']

# ## Source 1934-638
# ll = ['ON - PSK 1934-638',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_121001_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_121001_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_122807_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_155804_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_175504_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_121005_0001',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_121005_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_122811_0003',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_155808_0003',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_175509_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_121009_0001',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_121009_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_122815_0003',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_155812_0003',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_175513_0006',
#       'OFF',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_121001_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_121001_0009',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_122807_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_155804_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_175504_0009',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_121005_0004',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_121005_0009',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_122811_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_155808_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_175509_0009',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_121009_0004',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_121009_0009',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_122815_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_155812_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_175513_0009',
#       'ON - QSO B0521-365',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0010',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0016',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0029',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0004',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0010',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0016',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0029',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0004',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0010',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0016',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0029',
#       'OFF',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0007',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0013',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0019',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_195710_0032',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0007',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0013',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0019',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_195714_0032',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0007',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0013',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0019',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_195718_0032',
#       'ON - QSO B1145-676',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0009',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0018',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0024',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0003',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0009',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0018',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0024',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0003',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0009',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0018',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0024',
#       'OFF',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0012',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0021',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E2_205821_0027',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0006',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0012',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0021',
#       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E2_205825_0027',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0006',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0012',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0021',
#       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E2_205829_0027']

## Source 1934-638
# ll = ['ON - PSK 1934-638',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0002',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0005',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0007',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0008',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0009',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0010',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0002',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0005',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0002',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0005',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0007',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0008',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0002',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0005',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0007',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0008',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0009',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0010',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0011',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0001',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0002',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0003',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0004',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0005',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0006',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0007',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0008',
#       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0009']

## Source 1934-638
ll = ['ON - PSK 1934-638',
       'ESU1',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0001', #ON
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0002', #OFF
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0003', #ON
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0004', #OFF
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0005', #OFF
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0006', #ON
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0007', #OFF
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0008', #OFF
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_121005_0009', #OFF
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0001',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0002',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0003',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0004',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0005',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_122811_0006',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0001',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0002',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0003',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0004',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0005',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0006',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_155808_0007',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0001',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0002',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0003',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0004',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0005',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0006',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0007',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0008',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0009',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_175509_0010',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0001',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0002',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0003',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0004',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0005',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0006',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0007',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0008',
       '/home/taller-dis1/Angel/ESA/ESU2/MG12_NET4_2016_088_DD_E1_185557_0009',

       'ESU1',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0001', #ON
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0002', #OFF
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0003', #ON
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0004', #OFF
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0005', #OFF
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0006', #ON
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0007', #OFF
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0008', #OFF
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_121001_0009', #OFF
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0001',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0002',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0003',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0004',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0005',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_122807_0006',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0001',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0002',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0003',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0004',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0005',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0006',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_155804_0007',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0001',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0002',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0003',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0004',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0005',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0006',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0007',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0008',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0009',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_175504_0010',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0001',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0002',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0003',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0004',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0005',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0006',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0007',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0008',
       '/home/taller-dis1/Angel/ESA/ESU1/MG11_NET4_2016_088_DD_E1_185552_0009',

       'ESU3',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0001', #ON
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0002', #OFF
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0003', #ON
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0004', #OFF
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0005', #OFF
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0006', #ON
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0007', #OFF
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0008', #OFF
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_121009_0009', #OFF
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0001',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0002',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0003',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0004',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0005',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_122815_0006',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0001',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0002',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0003',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0004',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0005',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0006',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_155812_0007',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0001',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0002',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0003',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0004',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0005',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0006',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0007',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0008',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0009',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_175513_0010',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0001',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0002',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0003',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0004',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0005',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0006',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0007',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0008',
       '/home/taller-dis1/Angel/ESA/ESU3/MG13_NET4_2016_088_DD_E1_185601_0009'
     ]

try:
#     os.remove("/home/taller-dis1/outputCH0.dat")
#     os.remove("/home/taller-dis1/outputCH1.dat")
#     os.remove("/home/taller-dis1/outputCH2.dat")
#     os.remove("/home/taller-dis1/outputCH3.dat")
#     os.remove("/home/taller-dis1/output.dat")
#     os.remove("/home/taller-dis1/sky.dat")
    os.remove("/home/taller-dis1/*skytesting.dat")
#     os.remove("/home/taller-dis1/skytesting2.dat")
#     os.remove("/home/taller-dis1/IQskytesting.dat")
    print("Files Removed!")
except:
    print "No files to delete"


# PERIOD=int((17.5e6)/(176))

for filename in ll:
    print filename
    if filename.startswith('ON'):
        continue
    if filename.startswith('OFF'):
        continue
    if filename.startswith('ESU'):
        outputfile="/home/taller-dis1/"+filename+"_skytesting.dat"
        print outputfile
        continue
    
    b = os.path.getsize(filename)
    if os.path.getsize(filename) < 9.5e+7 :
        print "File less than 95Mb, missing data."
        print filename
        continue
    
    data,timearray,gaincfe,gaindigital,nblocks=readdatabytes(filename)
    
    if len(gaincfe) == nblocks:
        print "OK",nblocks
    
    ch0,ch1,ch2,ch3 = demux(data)
    
    dt = np.dtype(np.int16)
    dt = dt.newbyteorder('>')
    
    CH0,CH1,CH2,CH3 = (np.zeros(len(ch0)/32) for _ in xrange(4))
    
    CH0=np.frombuffer(ch0, dtype=dt)
    CH1=np.frombuffer(ch1, dtype=dt)
    CH2=np.frombuffer(ch2, dtype=dt)
    CH3=np.frombuffer(ch3, dtype=dt)

    CH0_fix,CH1_fix,CH2_fix,CH3_fix = (np.zeros(len(CH0)/2) for _ in xrange(4))

    channel0,channel1,channel2,channel3 = (np.zeros(len(CH0)) for _ in xrange(4))
    
    
    CH0I=CH0[::2]+0.5
    CH0Q=CH0[1::2]+0.5
    CH1I=CH1[::2]+0.5
    CH1Q=CH1[1::2]+0.5
    CH2I=CH2[::2]+0.5
    CH2Q=CH2[1::2]+0.5
    CH3I=CH3[::2]+0.5
    CH3Q=CH3[1::2]+0.5
    
    ### Calculate Power
    CH0_fix=np.square(CH0I)+np.square(CH0Q)
    CH1_fix=np.square(CH1I)+np.square(CH1Q)
    CH2_fix=np.square(CH2I)+np.square(CH2Q)
    CH3_fix=np.square(CH3I)+np.square(CH3Q)
    
    ### Mapping factor (2**15-1)**2
    #ampCH0=CH0_fix/1073676289
    #ampCH1=CH1_fix/1073676289
    #ampCH2=CH2_fix/1073676289
    #ampCH3=CH3_fix/1073676289
    
##  ### Gain correction in dBm
    gain=gaindigital*0.1+gaincfe*0.1
    ampCH0=gain+mw_to_dbm(CH0_fix)
    ampCH1=gain+mw_to_dbm(CH1_fix)
    ampCH2=gain+mw_to_dbm(CH2_fix)
    ampCH3=gain+mw_to_dbm(CH3_fix)

    ### Gain correction in mW
    ### Revert AGC in mW
#     gain=dbm_to_mw(gaindigital*0.1)*dbm_to_mw(gaincfe*0.1)
#     ampCH0=CH0_fix*gain
#     ampCH1=CH1_fix*gain
#     ampCH2=CH2_fix*gain
#     ampCH3=CH3_fix*gain
    
    ### Revert AGC in mW
    #Pi=Po/dbm_to_mw(gaindigital*0.1+gaincfe*0.1)
    
#    gain=dbm_to_mw(gaindigital*0.1)*1./dbm_to_mw(gaincfe*0.1)
#    gain=1./dbm_to_mw(gaindigital*0.1+gaincfe*0.1)
#    ampCH0=CH0_fix*gain
#    ampCH1=CH1_fix*gain
#    ampCH2=CH2_fix*gain
#    ampCH3=CH3_fix*gain

    # split 56 ~ 1sec
    # split 56*2 ~ 500 msec
    # split 56*4 ~ 250 msec
    #SPLIT=56*128 # ~ 10 umsec
    SPLIT=56
    tt=np.array_split(timearray, SPLIT)
    times=np.asarray([np.max(x) for x in tt])
    
    y=np.array_split(ampCH0, SPLIT)
    channel0=np.asarray([np.mean(x) for x in y])
    
    y=np.array_split(ampCH1, SPLIT)
    channel1=np.asarray([np.mean(x) for x in y])
    
    y=np.array_split(ampCH2, SPLIT)
    channel2=np.asarray([np.mean(x) for x in y])
                        
    y=np.array_split(ampCH3, SPLIT)
    channel3=np.asarray([np.mean(x) for x in y])
    
    with open(outputfile,'a') as ff:
        np.savetxt(ff, np.c_[times, channel0, channel1, channel2, channel3])
    
#     with open("/home/taller-dis1/IQskytesting.dat",'a') as ff:
#         np.savetxt(ff, np.c_[timearray,CH0I,CH0Q,CH1I,CH1Q,CH2I,CH2Q,CH3I,CH3Q])

print "Done!"