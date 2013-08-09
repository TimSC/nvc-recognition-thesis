#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt

N = 5
menMeans = (109, 140, 93, 65, 120)



ind = np.arange(N)  # the x locations for the groups
width = 0.5       # the width of the bars


plt.subplot(111)
rects1 = plt.bar(ind, menMeans, width,
                    color='r')

# add some
plt.ylabel('Number of Clips')
plt.title('Numbers of Manually Select Clips by NVC Category')
plt.xticks(ind+width/2., ('agree', 'understand', 'thinking', 'question', 'random') )

#plt.legend( (rects1[0], rects2[0]), ('Men', 'Women') )

plt.ylim([0,150])

plt.show()

