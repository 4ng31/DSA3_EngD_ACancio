
# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Plot data with different styles
"""

import numpy as np

from vispy.plot import Fig
fig = Fig()
ax_left = fig[0, 0]
ax_right = fig[0, 1]

import numpy as np
data = np.random.randn(2, 10)
ax_left.plot(data)
ax_right.histogram(data[1])