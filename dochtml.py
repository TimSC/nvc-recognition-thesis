
import xml.etree.ElementTree as ET
import HTMLParser, string
import os, shutil
from PIL import Image

def ReplaceMacros(el, defs, warn):

	for elc in el:
		ReplaceMacros(elc, defs, warn)

		if elc.tag != "macro":
			continue

		val = elc.attrib['v']
		elc.tag = "span"
		elc.attrib = {}
		if val in defs:
			elc.text = defs[val]
		else:
			elc.text = "Undefined("+unicode(val)+")"
			if val not in warn:
				print "Undefined macro", val
				warn.add(val)

def PreprocessXml(root):
	root2 = ET.Element("html")
	
	for el in root:
		if el.tag == "include":
			tree = ET.parse(el.attrib['file'])
			for el2 in tree.getroot():
				root2.append(el2)
		else:
			root2.append(el)

	return root2

##################################################

def ProcessSectionsRec(el, currentSection, depth, labels, numbering, numberedEls):
	
	for elc in el:
		if elc.tag not in ['chapter', 'section', 'subsection']:
			continue
		
		numbered = True
		if 'numbered' in elc.attrib and elc.attrib['numbered'] == "no":
			numbered = False

		while depth+1 > len(currentSection):
			currentSection.append(0)
			increasedDepth = True
		while depth+1 < len(currentSection):
			currentSection.pop()
	
		if numbered:
			currentSection[depth] += 1

		#print elc.tag, depth, currentSection

		labelNum = 1
		while labelNum > 0:
			if labelNum == 1:
				labelTxt = "label" 
			else:
				labelTxt = "label"+str(labelNum)
			if labelTxt in elc.attrib:
				labels[elc.attrib[labelTxt]] = elc
				labelNum += 1
			else:
				labelNum = 0

		numbering[id(elc)] = currentSection[:]
		numberedEls[id(elc)] = elc

		ProcessSectionsRec(elc, currentSection, depth+1, labels, numbering, numberedEls)

def ProcessSections(root, labels):

	currentSection = []
	numbering = {}
	numberedEls = {}

	ProcessSectionsRec(root, currentSection, 0, labels, numbering, numberedEls)

	for elnum in numberedEls:
		el = numberedEls[elnum]
		num = numbering[elnum]
		if 'title' not in el.attrib:
			continue
		title = ET.Element("h"+str(len(num)+1))
		titleTxt = ""
		for i in range(len(num)):
			if i > 0:
				titleTxt += "."
			titleTxt += str(num[i])

		h = HTMLParser.HTMLParser()
		titleTxt += " "+h.unescape(el.attrib['title'])

		title.text = titleTxt
		el.insert(0, title)

	return numbering, numberedEls

#########################################

def RemoveTempTagsRec(el):

	rem = []
	for elc in el:
		if elc.tag=="cite":
			rem.append(elc)
	
		RemoveTempTagsRec(elc)

	for elc in rem:
		el.remove(elc)

def RemoveTempTags(root):
	
	RemoveTempTagsRec(root)


########################################

def NumberFloating(el, tag, tagStack, labels, numbering, lastChapter, chapterCount, floatNums, floatLabels):

	for elc in el:
		currentSection = None
		for s in tagStack:
			if id(s) in numbering:
				currentSection = numbering[id(s)]
		if currentSection is not None and lastChapter != currentSection[0]:
			lastChapter = currentSection[0]
			chapterCount[0] = 0
		if currentSection is None:
			lastChapter = None
			chapterCount[0] = 0

		if tag == elc.tag:
			chapterCount[0] += 1
			#print "label", tag, currentSection, chapterCount[0]
			floatNums[id(elc)] = [currentSection[0], chapterCount[0]]

			labelNum = 1
			while labelNum > 0:
				if labelNum == 1:
					labelTxt = "label" 
				else:
					labelTxt = "label"+str(labelNum)
				if labelTxt in elc.attrib:
					floatLabels[elc.attrib[labelTxt]] = elc
					labelNum += 1
				else:
					labelNum = 0

		tmp = tagStack[:]
		tmp.append(elc)
		NumberFloating(elc, tag, tmp, labels, numbering, lastChapter, chapterCount, floatNums, floatLabels)

def FormatFloats(el, tag, floatNums, floatLabels):

	for elc in el:
		FormatFloats(elc, tag, floatNums, floatLabels)

		if tag != elc.tag:
			continue

		if elc.tag == "table":
			replaceTable = ET.Element("table")
			replaceTable.attrib['border'] = "2"
			rows = []
			for row in elc:
				replaceTable.append(row)
				rows.append(row)
			elc.append(replaceTable)

			for row in rows:
				elc.remove(row)

		captionTxt = None
		if 'caption' in elc.attrib:	
			captionTxt = elc.attrib['caption']
		elc.tag = "div"
		elc.attrib = {}
		elc.attrib['class'] = tag

		capt = ET.Element("p")
		capt.text = ""
		if id(elc) in floatNums:
			capt.text += string.capwords(tag)+" "
			for i, se in enumerate(floatNums[id(elc)]):
				if i > 0:
					capt.text+="."
				capt.text += str(se)
			capt.text += " "
			
		if captionTxt is not None:
			capt.text += captionTxt
		elc.append(capt)

#########################################

def ProcessReferencesRec(el, refs):

	for elc in el:
		if elc.tag=="cite":
			refsTxt = elc.attrib['ref']
			refLi = refsTxt.split(",")
			refLiCl = map(string.strip, refLi)
			refs.append((elc, refLiCl))
	
		ProcessReferencesRec(elc, refs)

def ProcessReferences(root):
	
	refs = []
	ProcessReferencesRec(root, refs)
	for (elc, refLiCl) in refs:
		elc.tag = "i"
		elc.text = "["
		for rnum, r in enumerate(refLiCl):
			if rnum > 0:
				elc.text += ", "
			elc.text += r
		elc.text += "]"
#############################################

def ReplaceLabelRefs(el, labels, numbering, numberedEls, floatNums, floatLabels):

	for elc in el:
		ReplaceLabelRefs(elc, labels, numbering, numberedEls, floatNums, floatLabels)

		if elc.tag != "ref":
			continue

		#print elc.attrib
		num = None
		if elc.attrib['label'] in labels:
			el = labels[elc.attrib['label']]
			num = numbering[id(el)]
		if elc.attrib['label'] in floatLabels:
			el = floatLabels[elc.attrib['label']]
			num = floatNums[id(el)]

		if num is None:
			print "Warning, label not found:", elc.attrib['label']
		
		elc.tag="span"
		elc.attrib = {}
		elc.text = ""
		if num is not None:
			for i, n in enumerate(num):
				if i > 0:
					elc.text += "."
				elc.text += str(n)
		else:
			elc.text = "??"

###############################################

def ReplaceGraphics(el, fili):
	for elc in el:
		ReplaceGraphics(elc, fili)
		if elc.tag != "graphic":
			continue
		width = None
		if 'width' in elc.attrib:
			width = float(elc.attrib['width'])

		fibase, ext = os.path.splitext(elc.text)
		pth = os.path.split(elc.text)
		pth2 = os.path.split(fibase)
		
		if ext != ".pdf":

			fina = "res/"+pth[-1]
			shutil.copyfile(elc.text, fina)
			assert fina not in fili
			fili.add(fina)

			im = Image.open(fina)
			print im.size

			elc.tag = "img"
			elc.attrib = {}
			elc.attrib['src'] = fina
			elc.text = ""
			if 'caption' in el.attrib:
				elc.attrib['alt'] = el.attrib['caption']
				elc.attrib['title'] = el.attrib['caption']
		else:
			fina = "res/"+pth2[-1]+".svg"
			if not os.path.isfile(fina):
				os.system("pdf2svg "+elc.text+" "+fina)

			elc.tag = "object"
			elc.attrib = {}
			elc.attrib['data'] = fina
			elc.attrib['type'] = "image/svg+xml"
			elc.text = "SVG Graphic"
			if 'caption' in el.attrib:
				elc.attrib['alt'] = el.attrib['caption']
				elc.attrib['title'] = el.attrib['caption']

#############################################

def CollectFootnotesRec(el, foot):
	for elc in el:
		if elc.tag == "footnote":
			foot.append((elc, elc.text))
			elc.tag = "span"
			elc.attrib['style'] = "font-size:xx-small; vertical-align:top;"
			elc.text = str(len(foot))

		CollectFootnotesRec(elc, foot)

def CollectFootnotes(el):
	foot = []	
	CollectFootnotesRec(el, foot)
	footnoteSec = ET.Element("div")

	footnoteTitle = ET.Element("h3")
	footnoteTitle.text="Footnotes"
	footnoteSec.append(footnoteTitle)

	for i, fo in enumerate(foot):
		footEl = ET.Element("div")
		footEl.text = str(i+1)+" "+fo[1]

		fos = []
		for ch in fo[0]:
			footEl.append(ch)
			fos.append(ch)
		for f in fos:
			fo[0].remove(f)

		footnoteSec.append(footEl)

	el.append(footnoteSec)


#####################################


def DefineAbbrevs(el, acro):
	for elc in el:
		DefineAbbrevs(elc, acro)

		if elc.tag == "ac" or elc.tag == "acf" or elc.tag == "acl" or elc.tag == "acf":
			tx = elc.text
			full = False
			if 'full' in elc.attrib and elc.attrib['full']=="yes":
				full = True

			elc.tag = "span"
			elc.attrib = {}
			if elc.text in acro:
				elc.attrib['title'] = acro[elc.text]
				elc.attrib['style'] = "cursor:help;border-bottom:1px dashed blue;"
			else:
				print "Abbreviation not defined:", elc.text

#########################################

if __name__ == "__main__":
	
	tree = ET.parse('thesis.xml')
	root = tree.getroot()

	defsXml = ET.parse('defs.xml')
	defs = {}
	for el in defsXml.getroot():
		k, v = None, None		
		for elc in el:
			if elc.tag == "k": k = elc.text
			if elc.tag == "v": v = elc.text
		defs[k] = v

	acroXml = ET.parse('acronym.xml')
	acro = {}
	for el in acroXml.getroot():
		k, v = None, None		
		for elc in el:
			if elc.tag == "k": k = elc.text
			if elc.tag == "v": v = elc.text
		acro[k] = v

	root2 = PreprocessXml(root)
	ReplaceMacros(root2, defs, set())

	#for el in root2:
	#	print el.tag

	labels = {}
	numbering, numberedEls = ProcessSections(root2, labels)

	ProcessReferences(root2) #Citations
	ReplaceGraphics(root2, set())

	floatNums = {}
	floatLabels = {}
	NumberFloating(root2, "table", [], labels, numbering, None, [None], floatNums, floatLabels)
	NumberFloating(root2, "figure", [], labels, numbering, None, [None], floatNums, floatLabels)
	NumberFloating(root2, "algorithm", [], labels, numbering, None, [None], floatNums, floatLabels)

	FormatFloats(root2, "table", floatNums, floatLabels)
	FormatFloats(root2, "figure", floatNums, floatLabels)
	FormatFloats(root2, "algorithm", floatNums, floatLabels)

	ReplaceLabelRefs(root2, labels, numbering, numberedEls, floatNums, floatLabels)
	CollectFootnotes(root2)
	DefineAbbrevs(root2, acro)

	out = open("out.html","w")
	out.write(ET.tostring(root2))
	out.close()

