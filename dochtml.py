
import xml.etree.ElementTree as ET
import HTMLParser, string

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

		print elc.tag, depth, currentSection

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
			print "label", tag, currentSection, chapterCount[0]
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

		elc.tag = "div"

		capt = ET.Element("p")
		capt.text = ""
		if id(elc) in floatNums:
			capt.text += string.capwords(tag)+" "
			for i, se in enumerate(floatNums[id(elc)]):
				if i > 0:
					capt.text+="."
				capt.text += str(se)
			capt.text += " "
			
		if 'caption' in elc.attrib:	
			capt.text += elc.attrib['caption']
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

		print elc.attrib
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

#########################################

if __name__ == "__main__":
	
	tree = ET.parse('thesis.xml')
	root = tree.getroot()

	root2 = PreprocessXml(root)

	for el in root2:
		print el.tag

	labels = {}
	numbering, numberedEls = ProcessSections(root2, labels)

	ProcessReferences(root2) #Citations

	floatNums = {}
	floatLabels = {}
	NumberFloating(root2, "table", [], labels, numbering, None, [None], floatNums, floatLabels)
	NumberFloating(root2, "figure", [], labels, numbering, None, [None], floatNums, floatLabels)
	NumberFloating(root2, "algorithm", [], labels, numbering, None, [None], floatNums, floatLabels)

	FormatFloats(root2, "table", floatNums, floatLabels)
	FormatFloats(root2, "figure", floatNums, floatLabels)
	FormatFloats(root2, "algorithm", floatNums, floatLabels)

	ReplaceLabelRefs(root2, labels, numbering, numberedEls, floatNums, floatLabels)

	out = open("out.html","w")
	out.write(ET.tostring(root2))
	out.close()

