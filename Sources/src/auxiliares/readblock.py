
import datetime
import numpy as np
import os
import mmap
import struct
from bitstring import BitStream, ConstBitStream,Bits
from bitstring import BitArray as bt
from bitarray import bitarray as BitArray

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

def copypost(src, dst, offset):
    with open(src, 'rb') as fd:
        mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
        with open(dst, 'ab') as f2:
            f2.write(mm[offset:])

def copyprev(src,dst, offset):
    with open(src, 'rb') as fd:
        mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
        with open(dst, 'ab') as f2:
            f2.write(mm[0:offset])
    
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


def datareduce(schdtimes,filelist,filetimes,scannumber,output):

    output="%s%s_scan%04d.bin" % (output, '_'.join((filelist[0].split('/')[-1]).split('_')[:-1]), scannumber)
    print(filelist)
    print(filetimes)
    print(schdtimes)
    print(output)
    
    for i in np.arange(2):
        print 'ok'
        with open(filelist[i]) as fd:
            mm = mmap.mmap(fd.fileno(), 0, prot=mmap.PROT_READ)
            header = readheader(mm[0:76],hprint=None)

        fs=header["samplerate"]
        qu=header["qu"]
        
        if qu == 5: #16-bits
            nsamples=87
        
        freq=17500000./(fs)
        timefilestart=filetimes[i]
        filename=filelist[i]
        
        filesize=os.path.getsize(filename)
        
        blocksize=1468
        N=float(filesize)/blocksize
        T=1./freq
        sec=T*nsamples*N
        
        ## Calculate end time file (next startimefie)
        delta=datetime.timedelta(seconds=sec)
        
#         tschdstart=datetime.datetime.strptime(schdtimes[0],'%Y-%m-%d %H:%M:%S')
        tschdstart=schdtimes[0]
#         tschdend=datetime.datetime.strptime(schdtimes[1],'%Y-%m-%d %H:%M:%S')
        tschdend=schdtimes[1]
        
#         tfilestart=datetime.datetime.strptime(timefilestart,'%Y-%m-%d %H:%M:%S.%f')
        tfilestart=timefilestart
        tfileend=tfilestart+delta
        
        
        print tfilestart, tschdstart, tfileend
        ## Lower bound
        if  tfilestart < tschdstart < tfileend:
            tdiff = tschdstart-tfilestart
            tdiff = tdiff.seconds+1e-6*tdiff.microseconds
            N1 = int(tdiff/(T*87))
            offset=blocksize*N1
            #### Bytes Offset file
            copypost(filename,output,offset)
        
        ## Upper bound        
        if  tfilestart < tschdend < tfileend:
            tdiff = tschdend-tfilestart
            tdiff = tdiff.seconds+1e-6*tdiff.microseconds
            N1 = int(tdiff/(T*87))
            offset=blocksize*N1
            #### Bytes Offset file
            copyprev(filename,output,offset)
    
# def main(args):iles
#     schdtimes=args['schdtimes']
#     filelist=args['files']
#     filetimes=args['filetimes']
#     output='testing.bin'
#     datareduce(schdtimes,filelist,filetimes,output)
    
# if __name__ == "__main__":

#     schdtimes=['2017-09-11 22:45:00','2017-09-11 22:45:55']
#     files=['/nfs/server/OBS4/2017-255/ifms1/MG11_NET4_2017_254_EO_E1_224427_0001',
#            '/nfs/server/OBS4/2017-255/ifms1/MG11_NET4_2017_254_EO_E1_224427_0002']
#     filetimes=['2017-09-11 22:44:30.801819','2017-09-11 22:45:26.961422']
    
#     args ={'schdtimes':schdtimes,'files':files, 'filetimes':filetimes }
    
#     main(args)

    