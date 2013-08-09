from PIL import Image, ImageDraw
import numpy as np

def Proj(pt):
	pt2 = (pt[0], pt[1], 1.)
	aff = np.array([[200,10,200],[-6,250,80],[0,0,0]])
	pr = np.dot(aff, pt2)
	return pr[:2].tolist()

if __name__=="__main__":
	im = Image.open("lbp-face-grid.jpg")

	dr = ImageDraw.Draw(im)
	for i in range(11):
		x1 = 0.
		y1 = i / 10.
		x2 = 1.
		y2 = i / 10.
		pt1 = Proj((x1, y1))
		pt2 = Proj((x2, y2))
		print pt1 + pt2
		dr.line(pt1 + pt2, fill=(255,255,128))
	del dr

	dr = ImageDraw.Draw(im)
	for i in range(11):
		x1 = i / 10.
		y1 = 0
		x2 = i / 10.
		y2 = 1.
		pt1 = Proj((x1, y1))
		pt2 = Proj((x2, y2))
		print pt1 + pt2
		dr.line(pt1 + pt2, fill=(255,255,128))
	del dr

	im.save("lbp-face-grid-overlay.jpg")
