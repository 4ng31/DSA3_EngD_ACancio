
#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Update a simple plot as rapidly as possible to measure speed.
"""
import pycuda.autoinit
import pycuda.gpuarray as gpuarray
import numpy as np

import skcuda.fft as cu_fft

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph.ptime import time
app = QtGui.QApplication([])

p = pg.plot()
p.setWindowTitle('pyqtgraph example: PlotSpeedTest')
p.setRange(QtCore.QRectF(0, -10, 5000, 20)) 
p.setLabel('bottom', 'Index', units='B')
curve = p.plot()

N = 8192*1024

#data=np.array((a.astype(int)).tolist(),dtype=int)

ptr = 0
lastTime = time()
fps = None
def update():
    global curve, ptr, p, lastTime, fps
    x = np.asarray(np.random.rand(N), np.float32)
    x_gpu = gpuarray.to_gpu(x)
    xf_gpu = gpuarray.empty(N/2+1, np.complex64)
    plan_forward = cu_fft.Plan(x_gpu.shape, np.float32, np.complex64)
    cu_fft.fft(x_gpu, xf_gpu, plan_forward)
    a = np.abs((xf_gpu**2).get())
    data=a.astype(float)

#     curve.setData(data[ptr%10])
    curve.setData(data)
    ptr += 1
    
    now = time()
    dt = now - lastTime
    lastTime = now
    if fps is None:
        fps = 1.0/dt
    else:
        s = np.clip(dt*3., 0, 1)
        fps = fps * (1-s) + (1.0/dt) * s
    p.setTitle('%0.2f fps' % fps)
    
    app.processEvents()  ## force complete redraw for every plot
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)
    


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()