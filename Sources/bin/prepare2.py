
#Input for this software are a configuration file and a survey schedule in csv format.
import os
import glob
import pandas as pd
pd.set_option('display.width',512)
pd.options.mode.chained_assignment = None  # default='warn'
import multiprocessing as mp
import numpy as np
import argparse
import datetime
import mmap
import sys
import gc
from readblock import datareduce

def find(indexfile,start,end):
    dtypes={'datetime':np.datetime64, 'start_seconds':np.float64,'date':'str','start_ttime':'str','freq':np.float64,'filename':'str','start_byte':'int64','end_byte':'int64'}
    aa = pd.read_csv(indexfile,parse_dates={'datetime':['date','start_ttime']},
                     keep_date_col = True, 
                     index_col='datetime',dtype=dtypes)  
    columns = ['start_seconds','date','start_ttime','freq','start_byte','end_byte']
    aa.drop(columns, inplace=True, axis=1)
    aa.dropna(inplace=True)
    df = aa[(aa.index >= start) & (aa.index <= end)]
    return df

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


def equals(DF,DF1):
    try:
        pd.assert_frame_equal(DF, DF1)
        return True
    except:  # appeantly AssertionError doesn't catch all
        return False
        

def findUDP(indexfile,start,end):
    
    ### Search files corresponding to the valid survey time
    start=np.datetime64(start)
    end=np.datetime64(end)
   
    df=find(indexfile,start,end)
       
    if df.empty:
        dtypes={'datetime':np.datetime64,'filename':'str'}
        labels=['datetime','filename']
        E1=pd.DataFrame(np.nan,labels,dtypes)
        E2=pd.DataFrame(np.nan,labels,dtypes)
        return [E1,E2]
    
    A=False
    B=False
    newstart=start
    newend=end
    
    delta = np.timedelta64(1,'m')

    while 1:
        df1=df   
        
        if (df.index.values)[0] > start:
            newstart=start-delta
        else:
            A=True
            
        if (df.index.values)[-1]+delta < end:
            newend=end+delta 
        else:
            B=True
            
        if A&B:
            break    
            
        df=find(indexfile,newstart,newend)
        
        if equals(df,df1):
            break

    ### Separate the Polarization file list
    E1=df[df['filename'].str.contains('_E1_', case=True, flags=0, na=np.nan, regex=True)]
    E2=df[df['filename'].str.contains('_E2_', case=True, flags=0, na=np.nan, regex=True)]
    
    return [E1,E2]

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

def readblocks(filename):
    import mmap
    if filename.split('_')[-1] == '0000':
        return []

    fsize=os.path.getsize(filename)
    if not fsize == 0:
        f= open(filename, 'rb')
        mm = mmap.mmap(f.fileno(), length=1468, offset=0, prot=mmap.PROT_READ)
    else:
        return ['NaN','NaN','NaN',filename,'0',fsize]
    
    while True:
        # Read Header (check cuantization and save timestamp)
        header = readheader(mm.read(76),hprint=None)
        ## Calculate UTC
        X=np.float64(header["timetag_samps"])*np.float64(1./17500000)
        Y=np.float64(header["path_delay"])*np.float64(1./35000000)
        utctime=np.float64(header["timetag_secs"])+X-Y
        ttime=sec2time(utctime,6)
        fs=header["samplerate"]
        mm.read(1392)
        break
    f.close()
    
    ## Generate DATE by YAR, DOY and TIME
    aux=filename.split('/')[-1]
    aux=aux.split('_')
    year=int(aux[2])
    doy=int(aux[3])
    starttime=int(aux[6])
    datetimestring= "%04d %03d %06d" % (year, doy, starttime)
    a=datetime.datetime.strptime(datetimestring, '%Y %j %H%M%S')

    datetimestring= "%04d %03d %s" % (year, doy, ttime)
    b=datetime.datetime.strptime(datetimestring, '%Y %j %H:%M:%S.%f')
    if a.strftime('%F%H%M%S') > b.strftime('%F%H%M%S'):
        doy=doy+1
   
    datetimestring= "%04d %03d %s" % (year, doy, ttime)
    c=datetime.datetime.strptime(datetimestring, '%Y %j %H:%M:%S.%f')
    ddate=c.strftime('%F')
    
    return [utctime,ddate,ttime,fs,filename,int(0),int(fsize)]
    
def genindex(indexfile,dirpath):
    import csv
    print dirpath
        
    ll=sorted(glob.glob(dirpath+'/*'))  
    pp = mp.Pool(6)
    results = pp.map(readblocks, ll, chunksize=1)
    pp.close()
    pp.join()
        
    with open(indexfile, 'wa') as f:
        fieldnames = ['start_seconds','date','start_ttime','freq','filename','start_byte','end_byte']
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(results)     
        
        
        
        
def main(args):
    schedulefile=args.schd
    configfile=args.config
    workdir=args.workdir
    surveypath=args.input
    
    ## This should be build with enabled IFMS
    indexfiles=[]
    if args.ifms in ("100", "101", "110", "111"):
        indexfiles.extend(['ifms1_index.csv'])
    if args.ifms in ("010", "011", "110", "111"):
        indexfiles.extend(['ifms2_index.csv'])
    if args.ifms in ("001", "011", "101", "111"):
        indexfiles.extend(['ifms3_index.csv'])
    if indexfiles == []:
        print 'No IFMS present'
        sys.exit()
        
        
    
    ## Generate First Index for the Survey
    for i in indexfiles:
        indexfile=workdir+i
        try:
            os.stat(workdir)
        except:
            os.makedirs(workdir)
        if os.path.isfile(indexfile):
            print 'Index OK'
        else: 
            print 'Index file doesn exist.'
            print 'Creating...',indexfile
            genindex(indexfile,surveypath+i.split('_')[0])
            
    ##########################################################################
    ## Find valid UDP
    headers = ['datetime', 'recordlength', 'source','frec_hz','resolution']
    dtypes = {'datetime': 'str', 'recordlength': 'float', 'source': 'str','frec_hz':'float', 'resolution':'int'}
    schd = pd.read_csv(schedulefile, header=None, names=headers, dtype=dtypes)
    
    
    
    ## Generate Data Schedule
    for idx in indexfiles:
        j=0
        Flag1=True
        Flag2=True
        for index, row in schd.iterrows():
            path=workdir+idx
             
            tstart=datetime.datetime.strptime(row['datetime'],'%Y/%m/%d/%H:%M:%S')
            tend=tstart+datetime.timedelta(seconds=row['recordlength'])
            
            E1,E2=findUDP(path,tstart.strftime("%Y-%m-%d %H:%M:%S.%f"),tend.strftime("%Y-%m-%d %H:%M:%S.%f"))
            E1.dropna(inplace=True)
            E2.dropna(inplace=True)
            if not E1.empty and not (E1.index.values[0] == 'datetime'):
                E1['SOURCE']=row['source']
                E1['SCAN']=j
                if not ( os.path.isfile(path+'gdsp1.csv') and Flag1):
                    E1.to_csv(path+'gdsp1.csv', mode='a', header=False)
                    Flag1=False
                
            if not E2.empty and not (E2.index.values[0] == 'datetime'):
                E2['SOURCE']=row['source']
                E2['SCAN']=j
                if not ( os.path.isfile(path+'gdsp2.csv') and Flag2):
                    E2.to_csv(path+'gdsp2.csv', mode='a', header=False)
                    Flag2=False
            j=j+1
            del E1
            del E2

    ##########################################################################
    ## Reduce
    
    ## Read SCHD File
    #df
    
    ## Read Index File
    for idx in indexfiles:
        path=workdir+idx
        for gdsp in ['gdsp1.csv','gdsp2.csv']:
            filetoread=path+gdsp
            if os.path.isfile(filetoread):
                print filetoread
                
                headers = ['timestamp','filename','source','scan']
                aa = pd.read_csv(filetoread,
                                 header=None,
                                 names = headers,
                                 parse_dates={'datetime':['timestamp']},
                                 #keep_date_col = True, 
                                 index_col='datetime'
                                )

##                for i in range(aa.scan.iat[0],aa.scan.iat[-1]+1,1):
##                    print i
##                    reduced=aa.loc[aa['scan'] == i]
##                    if not reduced.empty:
##                        filelist = reduced['filename'].tolist()
##                        filetimes = reduced.index.to_pydatetime().tolist()
##                        schdstart=datetime.datetime.strptime(schd.loc[i].datetime,'%Y/%m/%d/%H:%M:%S')
##                        schdend=schdstart+datetime.timedelta(seconds=schd.loc[i].recordlength)
##                        schdtimes = [schdstart, schdend ]
##                        scannumber=i
##                        datareduce(schdtimes,filelist,filetimes,scannumber,workdir)
                
                grouped = aa.groupby('scan')
                for name, group in grouped:
                    #print name
                    #print group
                    filelist = group['filename'].tolist()
                    filetimes = group.index.to_pydatetime().tolist()
                    schdstart=datetime.datetime.strptime(schd.loc[name].datetime,'%Y/%m/%d/%H:%M:%S')
                    schdend=schdstart+datetime.timedelta(seconds=schd.loc[name].recordlength)
                    schdtimes = [schdstart, schdend ]
                    scannumber=int(name)
                    datareduce(schdtimes,filelist,filetimes,scannumber,workdir)
                    
                del aa
                del grouped
                
            else:    
                print('Missing polarization')


if __name__ == "__main__":
    
    import time
    start_time = time.time()
    parser = argparse.ArgumentParser(description='Prepare recordered data for reducction.')
    parser.add_argument('-s', '--schedule', dest='schd',type=argparse.FileType('r'),
                        help='Read schedule file.', required=True)
    parser.add_argument('-c', '--config', dest='config',type=argparse.FileType('r'),
                        help='Read config file.', required=False)
    parser.add_argument('-o', '--workdir', dest='workdir',type=str,
                        help='Output directory PATH.', required=True)
    parser.add_argument('-i', '--input', dest='input',type=str,
                        help='Input directory PATH, Survey PATH.', required=True)
    parser.add_argument('-I', '--ifms', dest='ifms',type=str,
                        help='Enable: 1 Disable: 0, i.e 111 enables all IFMS 123 ', required=True)
    args = parser.parse_args()
    
    main(args)
    print("--- %s seconds ---" % (time.time() - start_time))