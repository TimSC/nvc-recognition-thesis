#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import csv

data = csv.DictReader(open("annotator_demographics.csv"))
culture1 = [x['gender'] for x in data]
plt.subplot(111)

labels = set(culture1)
freq = [culture1.count(x) for x in labels]
N = len(labels)

ind = np.arange(N)  # the x locations for the groups
width = 0.5       # the width of the bars

plt.pie(freq, labels=labels)

#plt.ylabel('Frequency')
#plt.title('Self-reported Primary Culture for Annotators')
#plt.xticks(ind+width/2., list(labels) )

#plt.legend( (rects1[0], rects2[0]), ('Men', 'Women') )

#plt.ylim([0,150])

plt.show()

