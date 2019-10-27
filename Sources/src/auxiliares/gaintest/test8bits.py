
import os
import sys
import numpy as np
from bitarray import bitarray
# from math import log10
# from astropy.table import Table, Column
# from astropy.io import ascii

print('Testing')

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

def readdatabytes(filename):
   """
   Notes
   =====
   
   """
   
   fsize=os.path.getsize(filename)
   print fsize
   
   datasize=int(fsize*1468)*1392 ## BYTES
   print datasize
   
   fh = bitarray()  
   da = bitarray(datasize*8) ### BITS
   da.setall(False)
   
   with open(filename, 'rb') as f:
       fh.fromfile(f)
   
   j=0
   i=0
   bits=8*1468
   
   while True:
       header = bitarray()
       data = bitarray()    

       aux=bits*i
       aux1=aux+8*76
       aux2=aux+bits
       
       header = fh[aux:aux1]    
       hd = readheader(header.tobytes(),hprint=False)
       print hd['magic']
#         if hd['magic'] == '\a3':
#             print('OK')
       
       if aux2 == len(fh):
           break
           
   return 0

readdatabytes('/home/taller-dis1/Angel/GSRF_TEST_2016_300_DD_E1_120158_0001')