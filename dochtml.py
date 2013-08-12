
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
			if labelTxt in el.attrib:
				labels[el.attrib[labelTxt]] = id(elc)
				labelNum += 1
			else:
				labelNum = 0

		numbering[id(elc)] = currentSection[:]
		numberedEls[id(elc)] = elc

		ProcessSectionsRec(elc, currentSection, depth+1, labels, numbering, numberedEls)

def ProcessSections(root):

	currentSection = []
	labels = {}
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


#########################################

if __name__ == "__main__":
	
	tree = ET.parse('thesis.xml')
	root = tree.getroot()

	root2 = PreprocessXml(root)

	for el in root2:
		print el.tag

	ProcessSections(root2)

	ProcessReferences(root2)

	out = open("out.html","w")
	out.write(ET.tostring(root2))
	out.close()

