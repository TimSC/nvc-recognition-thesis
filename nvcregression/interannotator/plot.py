import csv
import matplotlib.pyplot as plt

def GetScore(fiName, locIn, catIn):
	data = csv.reader(open(fiName))
	for li in data:
		loc = li[0]
		if loc == "Overall": continue
		cat = li[1]
		val = float(li[2])
		dev = float(li[3])
		if loc == locIn and cat == catIn:
			return val, dev	

	return None, None

def PlotLine(locIn, catIn):
	threshs = {1.0: "batchoutNone.txt", \
		0.28: "batchout0.28.txt",\
		0.25: "batchout0.25.txt",\
		0.20: "batchout0.2.txt",\
		0.15: "batchout0.15.txt",\
		0.10: "batchout0.1.txt",\
		0.05: "batchout0.05.txt"}
	pts = []
	for t in threshs:
		fina = threshs[t]
		yval, ydev = GetScore(fina, locIn, catIn)
		if yval is not None and ydev is not None:
			pts.append((t,yval,ydev))
	pts.sort()
	plt.errorbar([pt[0] for pt in pts], [pt[1] for pt in pts], yerr=[1.*pt[2] for pt in pts], label=locIn)

for cat in ["agree","understand","thinking","question"]:
	plt.clf()
	PlotLine("IND", cat)
	PlotLine("KEN", cat)
	PlotLine("GBR", cat)
	plt.legend(loc=4)
	plt.xlabel("Annotator Variance used to Filter Clips")
	plt.ylabel("Correlation Performance of Automatic System")
	plt.title(cat)
	plt.xlim([0.,1.1])

	plt.savefig("clipfilterperf-"+cat+".svg")
	#plt.show()



