
### RADSA MODULE
from bitarray import bitarray
import numpy as np

# MUX data
def mux(ch0,ch1,ch2,ch3):
    """Multiplex data and join channels into a single stream
    
    Notes7
    =====
    @param channel : channels with stream bits
    """
    b=bitarray(ch0.length()*2)
    c=bitarray(ch0.length()*2)
    stream=bitarray(ch0.length()*4)
    b.setall(False)
    c.setall(False)
    stream.setall(False)
       
    b[::2], b[1::2] = ch0, ch2
    c[::2], c[1::2] = ch1, ch3
    stream[::2], stream[1::2] = b, c
    
    return stream

# DeMUX data    
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
    
    ch0 = bitarray(stream.length()/4)
    ch1 = bitarray(stream.length()/4)
    ch2 = bitarray(stream.length()/4)
    ch3 = bitarray(stream.length()/4)
    ch0.setall(False)
    ch1.setall(False)
    ch2.setall(False)
    ch3.setall(False)

    b, c = stream[::2], stream[1::2]

    ch0, ch2 = b[::2], b[1::2]
    ch1, ch3 = c[::2], c[1::2]

    return ch0,ch1,ch2,ch3   

def decode2bit(ch0,ch1,ch2,ch3):
    import numpy as np
    # i.e. 2 bits and 2 bits for imaginary and real (I and Q)   
    d = {-2:bitarray('10'), 0:bitarray('00'),
         -1:bitarray('11'), 1:bitarray('01')}
    
    CH0=np.array(ch0.decode(d),dtype=np.int8)
    CH1=np.array(ch1.decode(d),dtype=np.int8)
    CH2=np.array(ch2.decode(d),dtype=np.int8)
    CH3=np.array(ch3.decode(d),dtype=np.int8)
    
    #Mapping
        
    return CH0,CH1,CH2,CH3
    
def decode4bit(ch0,ch1,ch2,ch3):
    # i.e. 4 bits and 4 bits for imaginary and real (I and Q) 
    dt = np.dtype(np.int8)
    dt = dt.newbyteorder('>')
    
    CH0=np.zeros((ch0.length()/4,), dtype=dt)
    CH1=np.zeros((ch0.length()/4,), dtype=dt)
    CH2=np.zeros((ch0.length()/4,), dtype=dt)
    CH3=np.zeros((ch0.length()/4,), dtype=dt)

    CH0[::2]  = np.bitwise_and(ch0, 0xf0).astype(dt) >> 4
    CH0[1::2] =(np.bitwise_and(ch0, 0x0f) << 4).astype(dt) >> 4
    CH1[::2]  = np.bitwise_and(ch1, 0xf0).astype(dt) >> 4
    CH1[1::2] =(np.bitwise_and(ch1, 0x0f) << 4).astype(dt) >> 4
    CH2[::2]  = np.bitwise_and(ch2, 0xf0).astype(dt) >> 4
    CH2[1::2] =(np.bitwise_and(ch2, 0x0f) << 4).astype(dt) >> 4
    CH3[::2]  = np.bitwise_and(ch3, 0xf0).astype(dt) >> 4
    CH3[1::2] =(np.bitwise_and(ch3, 0x0f) << 4).astype(dt) >> 4
    
    #Mapping
    
    
    return CH0,CH1,CH2,CH3
    
def decode8bit(ch0,ch1,ch2,ch3):
    # i.e. 8 bits and 8 bits for imaginary and real (I and Q) 
    dt = np.dtype(np.int8)
    dt = dt.newbyteorder('>')
    CH0=np.frombuffer(ch0, dtype=dt)
    CH1=np.frombuffer(ch1, dtype=dt)
    CH2=np.frombuffer(ch2, dtype=dt)
    CH3=np.frombuffer(ch3, dtype=dt)
    
    #Mapping
    
    return CH0,CH1,CH2,CH3

def decode16bit(ch0,ch1,ch2,ch3):
    from bitarray import bitarray
    # i.e. 16 bits and 16 bits for imaginary and real (I and Q) 
    dt = np.dtype(np.int16)
    dt = dt.newbyteorder('>')
    c0=np.frombuffer(ch0, dtype=dt)
    c1=np.frombuffer(ch1, dtype=dt)
    c2=np.frombuffer(ch2, dtype=dt)
    c3=np.frombuffer(ch3, dtype=dt)
    
    #Mapping
    CH0=c0.astype(np.float32)+0.5
    CH1=c1.astype(np.float32)+0.5
    CH2=c2.astype(np.float32)+0.5
    CH3=c3.astype(np.float32)+0.5
    
    return CH0,CH1,CH2,CH3 