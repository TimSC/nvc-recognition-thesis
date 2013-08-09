import csv, math
import numpy as np
import matplotlib.pyplot as plt

def OrderClips(data):
	out = []
	for li in data:
		clipId = li['clip_id']
		del li['clip_id']
		out.append((clipId, li))
	out.sort()
	return [a[1] for a in out]

def ComputeAverage(data, excludeAnnot = None):
	out = []
	for li in data:
		ratings = []
		for annot in li:
			if annot == excludeAnnot: continue
			rating = int(li[annot])
			if rating == -1: continue
			ratings.append(rating)
		out.append(np.array(ratings).mean())
	return out

def IsolateAnnot(data, findAnnot):
	out = []
	for li in data:
		ratings = None
		for annot in li:
			if annot != findAnnot: continue
			rating = int(li[annot])
			if rating != -1:
				ratings = rating
		out.append(ratings)
	return out

def CompareRatings(a, b):
	af, bf = [], []
	for av, bv in zip(a,b):
		if av is None or bv is None: continue
		af.append(av)
		bf.append(bv)
	return np.corrcoef(af,bf)[0,1]

dataAgree = csv.DictReader(open("../../annotation/twotalk/annotation_31/agree.csv"),delimiter="\t")
dataThinking = csv.DictReader(open("../../annotation/twotalk/annotation_31/thinking.csv"),delimiter="\t")
dataUnderstand = csv.DictReader(open("../../annotation/twotalk/annotation_31/understand.csv"),delimiter="\t")
dataQuestion = csv.DictReader(open("../../annotation/twotalk/annotation_31/question.csv"),delimiter="\t")

dataAgree = OrderClips(dataAgree)
dataThinking = OrderClips(dataThinking)
dataUnderstand = OrderClips(dataUnderstand)
dataQuestion = OrderClips(dataQuestion)
dataCats = [dataAgree, dataThinking, dataUnderstand, dataQuestion]

annotIds = dataAgree[0]
annotCorrel = []

for annotId in annotIds:
	catRatings = []
	fault = False
	for data1 in dataCats:
		annotRatings = IsolateAnnot(data1, annotId)
		otherRatings = ComputeAverage(data1, annotId)
		correl = CompareRatings(annotRatings, otherRatings)
		if math.isnan(correl): fault = True
		catRatings.append(correl)
	if not fault:
		print np.array(catRatings).mean()
		annotCorrel.append(np.array(catRatings).mean())

#ComputeAverage(dataAgree)
plt.hist(annotCorrel, bins=9)
plt.xlabel("Pearson's Correlation")
plt.ylabel("Number of Annotators")
plt.show()

