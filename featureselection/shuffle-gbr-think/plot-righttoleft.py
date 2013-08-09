
import matplotlib.pyplot as plt
import numpy as np
import csv

finame = "shufflefs-reverse-KEN-agree-1011.csv"

data = csv.reader(open(finame),delimiter="\t")
lines = [d for d in data]

x = [d[1] for d in lines]
seen = [d[2] for d in lines]
unseen = [d[3] for d in lines]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.plot(x,seen, 'b-')
ax.plot(x,unseen, 'r-')
#ax.set_title('test')
plt.xlabel("Number of Features in Mask")
plt.ylabel("Performance (Correlation)")

font = "sans-serif"
plt.text(1500, 0.3, "Unseen", ha="center", family=font, size=14)
plt.text(1500, 0.7, "Seen", ha="center", family=font, size=14)

plt.savefig(finame + ".pdf")
plt.show()

