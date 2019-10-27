import numpy as np
import pyqtgraph as pg
# import pyaudio
from PyQt4 import QtCore, QtGui

import sys

import pycuda.autoinit
import pycuda.gpuarray as gpuarray
import numpy as np

import skcuda.fft as cu_fft

FS = 100e3 #Hz 100kHz

CHUNKSZ = 1024 #samples


class recorder():
    def __init__(self, signal):
        self.signal = signal

    def read(self):
        N = CHUNKSZ
        ix = np.arange(N)
        A = 100
        f0 = 100000 #1kHz
        pure = A * np.sin(2 * np.pi * f0 * ix/float(N))
        noise = np.random.normal(0, 1, N)
        signal = pure + noise

        
        self.signal.emit(signal)

class SpectrogramWidget(pg.PlotWidget):
    read_collected = QtCore.pyqtSignal(np.ndarray)
    def __init__(self):
        super(SpectrogramWidget, self).__init__()

        self.img = pg.ImageItem()
        self.addItem(self.img)

        self.img_array = np.zeros((1000, CHUNKSZ/2+1))

        # bipolar colormap

        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.img.setLookupTable(lut)
        self.img.setLevels([-50,40])

        freq = np.arange((CHUNKSZ/2)+1)/(float(CHUNKSZ)/FS)
        print freq[0],'-',freq[-1]
        sys.exit()
        yscale = 1.0/(self.img_array.shape[1]/freq[-1])
        self.img.scale((1./FS)*CHUNKSZ, yscale)

        self.setLabel('left', 'Frequency', units='kHz')

        self.win = np.hanning(CHUNKSZ)
        self.show()

    def update(self, chunk):
        
        # normalized, windowed frequencies in data chunk
        
        data = chunk*self.win
        
        spec = np.fft.rfft(data.astype(np.float32))
        
#         x_gpu = gpuarray.to_gpu(data.astype(np.float32))
#         xf_gpu = gpuarray.empty(CHUNKSZ/2+1, np.complex64)
#         plan_forward = cu_fft.Plan(x_gpu.shape, np.float32, np.complex64)
#         cu_fft.fft(x_gpu, xf_gpu, plan_forward)
        
#         spec=xf_gpu.get()
        
        # get magnitude
        psd = abs(spec/CHUNKSZ)
        
        # convert to dB scale
        psd = 20 * np.log10(psd)
        
        print len(psd)

        # roll down one and replace leading edge with new data

        self.img_array = np.roll(self.img_array, -1, 0)
        self.img_array[-1:] = psd

        self.img.setImage(self.img_array, autoLevels=False)

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = SpectrogramWidget()
    w.read_collected.connect(w.update)

    IN = recorder(w.read_collected)

    # time (seconds) between reads

    interval = FS/CHUNKSZ
    t = QtCore.QTimer()
    t.timeout.connect(IN.read)
    t.start(1000/interval) #QTimer takes ms


    app.exec_()
#     mic.close()