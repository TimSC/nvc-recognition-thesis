import sys, string, codecs

def FindTagPos(li):

	startPos = string.find(li,"\\")
	if startPos == -1:
		return -1, -1

	pos = startPos
	scan = True
	bracket = False
	while scan:
		#print pos, li[pos]

		if pos >= len(li):
			scan = False
			continue

		if li[pos] == ' ' and not bracket:
			scan = False
			continue
			
		if li[pos] == '{':
			bracket = True

		if li[pos] == '}':
			bracket = False
			scan = False
			pos += 1
			continue

		pos += 1

	return startPos, pos

def GenReplacement(tag):
	print tag
	if tag[:4] == "\\ac{":
		return "<ac>"+tag[4:-1]+"</ac>"
	if tag[:5] == "\\acf{":
		return "<ac full='yes'>"+tag[5:-1]+"</ac>"
	if tag[:5] == "\\acl{":
		return "<ac long='yes'>"+tag[5:-1]+"</ac>"
	if tag[:6] == "\\cite{":
		return "<cite ref='"+tag[6:-1]+"'/>"
	if tag[:5] == "\\ref{":
		return "<ref label='"+tag[5:-1]+"'/>"
	if tag[:10] == "\\footnote{":
		return "<footnote>"+tag[10:-1]+"</footnote>"

	if string.find(tag, '{') != -1:
		print tag

	assert string.find(tag, '{') == -1
	return "<macro v='"+tag[1:]+"'/>"

def ReplaceTags(li):
	li = li[:]
	startPos, endPos = FindTagPos(li)
	while startPos != -1:
		tag = li[startPos:endPos] 
		tag2 = GenReplacement(tag)
		li = li[:startPos] + tag2 + li[endPos:]
		startPos, endPos = FindTagPos(li)
	return li

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "Specify file name for in and out"
		exit(0)

	finaIn = sys.argv[1]
	finaOut = sys.argv[2]

	fi = codecs.open(finaIn, "r", "utf-8")
	fiOut = codecs.open(finaOut, "wt", "utf-8")

	for li in fi:
		lia = li.replace("\"{o}",unichr(0x00F6))
		li2 = ReplaceTags(lia)
		li3 = string.replace(li2,"``",unichr(8220))
		li3 = string.replace(li3,"''",unichr(8221))
		fiOut.write(li3)
	


