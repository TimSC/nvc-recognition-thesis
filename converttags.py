import sys, string, codecs

def FindTagPos(li):

	startPos = string.find(li,"\\")
	if startPos == -1:
		return -1, -1

	while li[startPos+1] == "{" or li[startPos+1] == "}":
		startPos = string.find(li,"\\",startPos+1)
		if startPos == -1:
			return -1, -1

	pos = startPos
	scan = True
	bracket = 0
	while scan:
		#print pos, li[pos]
		pos += 1

		if pos >= len(li):
			scan = False
			continue

		if li[pos] in [' ','_','^','}','$','=','\\','<','>'] and bracket==0:
			scan = False
			continue
			
		if li[pos] == '{':
			bracket += 1

		if li[pos] == '}':
			bracket -= 1
			if bracket == 0:
				scan = False
				pos += 1
				continue


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
	if tag[:8] == "\\textit{":
		return "<i>"+tag[8:-1]+"</i>"
	if tag[:8] == "\\textbf{":
		return "<b>"+tag[8:-1]+"</b>"
	if tag[:10] == "\\footnote{":
		return "<footnote>"+tag[10:-1]+"</footnote>"

	if tag[:5] == "\\frac":
		return "#"+tag[1:]

	if string.find(tag, '{') != -1:
		print tag

		replaceTags = ["overline", "mathbb", "bar", "mathcal", "acs", "widehat"]
		for t in replaceTags:
			if tag[:len(t)+2] == "\\"+t+"{":
				return "<"+t+">"+tag[len(t)+2:-1]+"</"+t+">"

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
		if li[:3]=="eqn":
			fiOut.write(li)
			continue
		lia = li.replace("\"{o}",unichr(0x00F6))
		li2 = ReplaceTags(lia)
		li3 = string.replace(li2,"``",unichr(8220))
		li3 = string.replace(li3,"''",unichr(8221))
		fiOut.write(li3)
	


