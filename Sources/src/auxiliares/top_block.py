#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Test 8 bit IQ pure tone
# Author: Angel Cancio
# Description: Evaluate IQ waveform for 4 channels of a pure tone signal
# Generated: Thu Feb 22 12:27:07 2018
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx


class top_block(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Test 8 bit IQ pure tone")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = (17500000/32)

        ##################################################
        # Blocks
        ##################################################
        self.wxgui_fftsink2_0_0_0 = fftsink2.fft_sink_c(
        	self.GetWin(),
        	baseband_freq=70400000,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=True,
        	avg_alpha=0.5,
        	title='CH2',
        	peak_hold=True,
        	win=window.hanning,
        )
        self.GridAdd(self.wxgui_fftsink2_0_0_0.win, 1, 0, 1, 1)
        self.blocks_throttle_0_1 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_file_source_0_0_1 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/bgx/gnuradio/alfa/ch02.dat', True)

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0_0_1, 0), (self.blocks_throttle_0_1, 0))    
        self.connect((self.blocks_throttle_0_1, 0), (self.wxgui_fftsink2_0_0_0, 0))    

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.wxgui_fftsink2_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_1.set_sample_rate(self.samp_rate)


def main(top_block_cls=top_block, options=None):

    tb = top_block_cls()
    tb.Start(True)
    tb.Wait()


if __name__ == '__main__':
    main()