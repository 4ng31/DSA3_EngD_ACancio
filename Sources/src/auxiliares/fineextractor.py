
import os
import glob
import datetime
import mmap
import sys
import gc

import timeit

print 'Testing'

def readheader(BS,hprint=None):
    from bitstring import BitStream
    import struct
    b = BitStream('0x'+''.join(x.encode('hex') for x in struct.unpack('>72s',BS)))
    #magic = b.read(32).hex# 32 magic word
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


def createheader(filename,timetag_sec,timetag_samp,delay,deltaID,frequency,quantization,muxflag):
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

def readvalidbytes(filename,UDPstartbyte,validrecordedbytes):
    #Read block
    from bitarray import bitarray as BitArray
    import binascii
    
    fh = BitArray()  

    da = BitArray(validrecordedbytes)
    da.setall(False)

    
    with open(filename, 'rb') as f:
        fh.fromfile(f)
        
    i=0
    j=0
    first=True
    while True:
        header = BitArray()
        data = BitArray()    

        bits=8*1468
        aux=bits*i
        aux1=aux+8*76
        aux2=aux+bits
        
        header = fh[aux:aux1]
        
        if first:
            data = fh[aux1+UDPstartbyte*8:aux2]
            first=False
        else:
            data = fh[aux1:aux2]


        ### Check magic word
        mword =  binascii.hexlify(header[0:31])
        if mword != 'a3c725b6':
            print 'Wrong magic word' 
            print len(data)
            print len(header)
            sys.exit(1)

        i=i+1
    
        jold=j
        j=j+data.length()
        
        if j > validrecordedbytes*8:
            cut=validrecordedbytes*8-da.length()
            print cut
            da[jold:cut]=data[0:cut]           
            break
            
        da[jold:jold+data.length()]=data            
        
        if aux2 == len(fh):
            break

    print binascii.hexlify(header[0:31])

    with open(filename+'final.bin', 'ab') as f:
        da.tofile(f)
        
    db = BitArray()  
    with open(filename+'final.bin', 'rb') as f:
        db.fromfile(f)
    
    ### This comparison takes too long
    if da == db[30*8:]:
        print "OK"
    else:
        print "Wrong Output"
        
    print da.length()
    print db.length()
    

##### Input Values
### TimeInterval 71999.9996702 - 72055.9996702
### ID position
## idE11 68
## idE21 24
## idE31 4
## idE12 33
## idE22 67
## idE32 0

### Size Array Samples 5568182

### Bytes validos: 89090912

### Starting reading samples by udp packet
## bytesE11 1088
## bytesE21 384
## bytesE31 64
## bytesE12 528
## bytesE22 1072
## bytesE32 0

# ### This program have to read an extract all valid bytes and remove UDP headers.
# filename='/home/taller-dis1/Angel/ESA/test/cutfile/MG11_NET4_2016_088_DD_E1_195710_cut'
# UDPstartbyte=1088
# validrecordedbytes=89090912
# timetag_sec=71999
# timetag_samp=17484608
# delay=4534
# frequency=176
# deltaID=68
# quantization=16
# muxflag=1

# createheader(filename,timetag_sec,timetag_samp,delay,frequency,deltaID,quantization,muxflag)
# # readvalidbytes(filename,UDPstartbyte,arraysize=1)
# import timeit
# print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)", 
#                     setup = "from __main__ import readvalidbytes,  filename,UDPstartbyte,validrecordedbytes", 
#                     number=1)

# ### This program have to read an extract all valid bytes and remove UDP headers.
# filename='/home/taller-dis1/Angel/ESA/test/cutfile/MG12_NET4_2016_088_DD_E1_195714_cut'
# UDPstartbyte=384
# validrecordedbytes=89090912
# timetag_sec=71999
# timetag_samp=17492368
# delay=4534
# frequency=176
# deltaID=24
# quantization=16
# muxflag=1

# createheader(filename,timetag_sec,timetag_samp,delay,frequency,deltaID,quantization,muxflag)
# # readvalidbytes(filename,UDPstartbyte,arraysize=1)
# import timeit
# print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)", 
#                     setup = "from __main__ import readvalidbytes,  filename,UDPstartbyte,validrecordedbytes", 
#                     number=1)

# ### This program have to read an extract all valid bytes and remove UDP headers.
# filename='/home/taller-dis1/Angel/ESA/test/cutfile/MG13_NET4_2016_088_DD_E1_195718_cut'
# UDPstartbyte=64
# validrecordedbytes=89090912
# timetag_sec=71999
# timetag_samp=17495792
# delay=4534
# frequency=176
# deltaID=4
# quantization=16
# muxflag=1

# createheader(filename,timetag_sec,timetag_samp,delay,frequency,deltaID,quantization,muxflag)
# # readvalidbytes(filename,UDPstartbyte,arraysize=1)
# import timeit
# print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)", 
#                     setup = "from __main__ import readvalidbytes,  filename,UDPstartbyte,validrecordedbytes", 
#                     number=1)

# ### This program have to read an extract all valid bytes and remove UDP headers.
# filename='/home/taller-dis1/Angel/ESA/test/cutfile/MG11_NET4_2016_088_DD_E2_195710_cut'
# UDPstartbyte=528
# validrecordedbytes=89090912
# timetag_sec=71999
# timetag_samp=17490768
# delay=4534
# frequency=176
# deltaID=33
# quantization=16
# muxflag=1

# createheader(filename,timetag_sec,timetag_samp,delay,frequency,deltaID,quantization,muxflag)
# # readvalidbytes(filename,UDPstartbyte,arraysize=1)
# import timeit
# print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)", 
#                     setup = "from __main__ import readvalidbytes,  filename,UDPstartbyte,validrecordedbytes", 
#                     number=1)

# ### This program have to read an extract all valid bytes and remove UDP headers.
# filename='/home/taller-dis1/Angel/ESA/test/cutfile/MG12_NET4_2016_088_DD_E2_195714_cut'
# UDPstartbyte=1072
# validrecordedbytes=89090912
# timetag_sec=71999
# timetag_samp=17484800
# delay=4534
# frequency=176
# deltaID=67
# quantization=16
# muxflag=1

# createheader(filename,timetag_sec,timetag_samp,delay,frequency,deltaID,quantization,muxflag)
# # readvalidbytes(filename,UDPstartbyte,arraysize=1)
# import timeit
# print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)", 
#                     setup = "from __main__ import readvalidbytes,  filename,UDPstartbyte,validrecordedbytes", 
#                     number=1)

# ### This program have to read an extract all valid bytes and remove UDP headers.
# filename='/home/taller-dis1/Angel/ESA/test/cutfile/MG13_NET4_2016_088_DD_E2_195718_cut'
# UDPstartbyte=0
# validrecordedbytes=89090912
# timetag_sec=71999
# timetag_samp=17496496
# delay=4534
# frequency=176
# deltaID=0

quantization=16
muxflag=1

# createheader(filename,timetag_sec,timetag_samp,delay,frequency,deltaID,quantization,muxflag)
# # readvalidbytes(filename,UDPstartbyte,arraysize=1)
# import timeit
# print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)", 
#                     setup = "from __main__ import readvalidbytes,  filename,UDPstartbyte,validrecordedbytes", 
#                     number=1)



ll=['/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG11_NET4_2016_088_DD_E1_195710_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG12_NET4_2016_088_DD_E1_195714_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG13_NET4_2016_088_DD_E1_195718_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG11_NET4_2016_088_DD_E2_195710_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG12_NET4_2016_088_DD_E2_195714_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG13_NET4_2016_088_DD_E2_195718_cutfinal_ON2.bin']

##### ON #####
#72359.9996647 - 72415.9996647

##### OFF #####
#72539.999662 - 72595.999662


deltaID=[68, 24, 4, 33, 67, 0]
UDPsb = [1088, 384, 64, 528, 1072, 0]
validrecordedbytes=89090912

j=0
for i in ll:
    
        with open(i,'rb') as ff:
            MW=ff.read(4)
            HD=ff.read(72)
            header = readheader(HD,hprint=None)
        print i,header['timetag_secs'],header['timetag_samps'],header['path_delay'],header["samplerate"],deltaID[j], quantization, muxflag 
        createheader(i,header['timetag_secs'],header['timetag_samps'],header['path_delay'],header["samplerate"],deltaID[j], quantization, muxflag)
        UDPstartbyte=UDPsb[j]
        filename=i
        print timeit.timeit("readvalidbytes(filename,UDPstartbyte,validrecordedbytes)",
                            setup = "from __main__ import readvalidbytes, filename,UDPstartbyte,validrecordedbytes", 
                            number=1)
        j=j+1