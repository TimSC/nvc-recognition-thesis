#!/usr/bin/env python
import numpy.numarray as na

from pylab import *

labels = ["Mean Only", "Variance Only", "Mean and Variance"]
data =   [0.2658333333, 0.135, 0.3058333333]

xlocations = na.array(range(len(data)))+0.5
width = 0.5
bar(xlocations, data, width=width)
#yticks(range(0, 8))
xticks(xlocations+ width/2, labels)
xlim(0, xlocations[-1]+width*2)
#title("Average Ratings on the Training Set")
#gca().get_xaxis().tick_bottom()
#gca().get_yaxis().tick_left()

show()

