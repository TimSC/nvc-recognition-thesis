
import xml.etree.ElementTree as ET

def PreprocessXml(root):
	
	for elnum in range(len(root)):
		print root[elnum].tag
		el = root[elnum]
		if el.tag == "include":
			tree = ET.parse(el.attrib['file'])
			root[elnum] = tree.getroot()

if __name__ == "__main__":
	
	tree = ET.parse('thesis.xml')
	root = tree.getroot()

	root2 = PreprocessXml(root)

	for el in root2:
		print el.tag

