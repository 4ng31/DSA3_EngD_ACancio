
#Input for this software are a configuration file and a survey schedule in csv format.
import os
import glob
import pandas as pd
pd.set_option('display.width',512)
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import datetime
import mmap
import sys
import gc

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


def readblocks2(filename,start,end):
    with open(filename, 'rb') as f:
        fsize=os.path.getsize(filename)
        if not fsize == 0:
            # memory-map the file, size 0 means whole file
            mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        else:
            return ['NaN','NaN','NaN',filename,'0',int(fsize)]

        mm.seek(start)
        position=mm.tell()
#         print position
        a=0
        while True:
            # Magic Word
            byte=mm.read(4)
            if not byte:
                break
            # Read Header (check cuantization and save timestamp)
            header = readheader(mm.read(72),hprint=None)
            ## Calculate UTC
            X=np.float64(header["timetag_samps"])*np.float64(1./17500000)
            Y=np.float64(header["path_delay"])*np.float64(1./35000000)
            utctime=np.float64(header["timetag_secs"])+X-Y
            ttime=sec2time(utctime,6)
            fs=header["samplerate"]
            mm.read(1392)
            
            ### Copy data to new file
            
            
            if a == 0:
                print ttime,fs,filename,start,mm.tell()
                a=1
            
            if end-1468*2 == mm.tell():
                print ttime,fs,filename,end-1468,mm.tell()
                break
            mm.seek(end-1468*3)
            position=mm.tell()
#             print position



    
def sync2(filename,start,end):
    a=0
    #Read block
    from bitarray import bitarray as BitArray
    with open(filename, 'rb') as f:
        # memory-map the file, size 0 means whole file
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        ll=[]
        while True:
            # Magic Word
            MW=mm.read(4)
            mw = BitArray()
            mw.frombytes(str(MW))
            if not MW:
                return 0
            
            # Read Header (check cuantization and save timestamp)
            HD=mm.read(72)
            hd = BitArray()
            hd.frombytes(str(HD))
            header = readheader(HD,hprint=None)
            
            ## Calculate UTC
            utctime=np.float64(header["timetag_secs"])+np.float64(header["timetag_samps"])*np.float64(1./17500000)-np.float64(header["path_delay"])*np.float64(1./35000000)
            sr=header["samplerate"]
            ttime=sec2time(utctime,6)
            
            ## Read 1392 bytes 
            mm.read(1392)
            if a == 0:
#                 print format(utctime, '.10f'),(17.5e6)/sr,header["timetag_secs"],header["timetag_samps"],header["path_delay"],',',ttime,',',sr
                ll.append([filename,utctime,(17.5e6)/sr,header["timetag_secs"],header["timetag_samps"],header["path_delay"],ttime,sr])
                a=1
                break # Just need first frame data
            
            if end == mm.tell():
#                 print format(utctime, '.10f'),(17.5e6)/sr,header["timetag_secs"],header["timetag_samps"],header["path_delay"],',',ttime,',',sr
                ll.append([filename,utctime,(17.5e6)/sr,header["timetag_secs"],header["timetag_samps"],header["path_delay"],ttime,sr])
                break
            mm.seek(end-1468)
            position=mm.tell()
#             print position
            
        return ll

def niceprint(the_list):
    from pprint import pprint
    pprint(the_list)

def truncate(n,dec):
    res=10**int(dec)
    n=int(n*res)
    n/=float(res)
    return n

def calcNsamples(delta,timetag_sec,timetag_samp,delay,UTCmax):
#     timetag_samp=17496496.
#     timetag_sec=71999.
    delta=176.
    UTC=timetag_sec+(timetag_samp)*(1./17500000)-float(delay)/35000000
    n=0
#     UTCmax=UTC+56.
    if UTC == UTCmax:
        return n

    while UTC < UTCmax:
        #    print UTC
        UTC=timetag_sec+(timetag_samp+delta*n)*(1./17500000)-float(delay)/35000000
#         print n,UTC
        n=n+1
       
    return n-1

print "##### ON #####"

ll=['/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG11_NET4_2016_088_DD_E1_195710_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG12_NET4_2016_088_DD_E1_195714_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG13_NET4_2016_088_DD_E1_195718_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG11_NET4_2016_088_DD_E2_195710_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG12_NET4_2016_088_DD_E2_195714_cutfinal_ON2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/ON/test/MG13_NET4_2016_088_DD_E2_195718_cutfinal_ON2.bin']

ESUs=[]

for i in ll:
    filename=i
    startpos=0
    endpos=os.path.getsize(filename)
    ESUs.extend(sync2(filename,start=startpos,end=endpos))
    
recordlength=56 ## Seconds

ttfirst=np.array([ESUs[0][1],ESUs[1][1],ESUs[2][1],ESUs[3][1],ESUs[4][1],ESUs[5][1]],dtype=np.float)
tref=ttfirst.max()
tfinal=tref+recordlength ## time recorded

print tref,'-',tfinal

idESUs=[]
# ###                 delta, timetag_sec,timetag_samp,delay,UTCmax
idESUs.append(calcNsamples(ESUs[0][2],ESUs[0][3],ESUs[0][4],ESUs[0][5],tref))
idESUs.append(calcNsamples(ESUs[1][2],ESUs[1][3],ESUs[1][4],ESUs[1][5],tref))
idESUs.append(calcNsamples(ESUs[2][2],ESUs[2][3],ESUs[2][4],ESUs[2][5],tref))
idESUs.append(calcNsamples(ESUs[3][2],ESUs[3][3],ESUs[3][4],ESUs[3][5],tref))
idESUs.append(calcNsamples(ESUs[4][2],ESUs[4][3],ESUs[4][4],ESUs[4][5],tref))
idESUs.append(calcNsamples(ESUs[5][2],ESUs[5][3],ESUs[5][4],ESUs[5][5],tref))

print idESUs
ix=(np.asarray(idESUs)).argmin()
# ## Calculate length sample array
nsamples=calcNsamples(ESUs[ix][2],ESUs[ix][3],ESUs[ix][4],ESUs[ix][5],tfinal)
print nsamples

# Fine valid bytes to read
bytes=(nsamples*128)/8
print 'Bytes validos:',bytes

# ### Demux files
BitSamples=128 ## 16-bit resolution

print 'Starting reading samples by udp packet'
print 'E11=0,E21=1,E31=2,E12=3,E22=4,E32=5'
for i in range(0,6,1):
    print i,idESUs[i]*BitSamples/8
    
    
print "##### OFF #####"

ll=['/home/taller-dis1/Angel/ESA/testing/Archivos/OFF/test/MG11_NET4_2016_088_DD_E1_195710_cutfinal_OFF2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/OFF/test/MG12_NET4_2016_088_DD_E1_195714_cutfinal_OFF2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/OFF/test/MG13_NET4_2016_088_DD_E1_195718_cutfinal_OFF2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/OFF/test/MG11_NET4_2016_088_DD_E2_195710_cutfinal_OFF2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/OFF/test/MG12_NET4_2016_088_DD_E2_195714_cutfinal_OFF2.bin',
    '/home/taller-dis1/Angel/ESA/testing/Archivos/OFF/test/MG13_NET4_2016_088_DD_E2_195718_cutfinal_OFF2.bin']

ESUs=[]

for i in ll:
    filename=i
    startpos=0
    endpos=os.path.getsize(filename)
    # readblocks2(filename,startpos,endpos)
    ESUs.extend(sync2(filename,start=startpos,end=endpos))
    
recordlength=56 ## Seconds

ttfirst=np.array([ESUs[0][1],ESUs[1][1],ESUs[2][1],ESUs[3][1],ESUs[4][1],ESUs[5][1]],dtype=np.float)
tref=ttfirst.max()
tfinal=tref+recordlength ## time recorded

print tref,'-',tfinal

idESUs=[]
# ###                 delta, timetag_sec,timetag_samp,delay,UTCmax
idESUs.append(calcNsamples(ESUs[0][2],ESUs[0][3],ESUs[0][4],ESUs[0][5],tref))
idESUs.append(calcNsamples(ESUs[1][2],ESUs[1][3],ESUs[1][4],ESUs[1][5],tref))
idESUs.append(calcNsamples(ESUs[2][2],ESUs[2][3],ESUs[2][4],ESUs[2][5],tref))
idESUs.append(calcNsamples(ESUs[3][2],ESUs[3][3],ESUs[3][4],ESUs[3][5],tref))
idESUs.append(calcNsamples(ESUs[4][2],ESUs[4][3],ESUs[4][4],ESUs[4][5],tref))
idESUs.append(calcNsamples(ESUs[5][2],ESUs[5][3],ESUs[5][4],ESUs[5][5],tref))

print idESUs
ix=(np.asarray(idESUs)).argmin()
# ## Calculate length sample array
nsamples=calcNsamples(ESUs[ix][2],ESUs[ix][3],ESUs[ix][4],ESUs[ix][5],tfinal)
print nsamples

# Fine valid bytes to read
bytes=(nsamples*128)/8
print 'Bytes validos:',bytes

# ### Demux files
BitSamples=128 ## 16-bit resolution

print 'Starting reading samples by udp packet'
print 'E11=0,E21=1,E31=2,E12=3,E22=4,E32=5'
for i in range(0,6,1):
    print i,idESUs[i]*BitSamples/8
    