import string
import sys
import os

delim = ',;,'
dictwords = dict()
listwords = []

f = open("dictionary")
i = 0
for line in f:
	line = line.strip()
	dictwords[line] = i
	i += 1
	listwords.append(line)
f.close()

title = ['Drug1', 'Drug2', 'Head1', 'Head2', '#words b/w 1 & 2']
title.extend(map(lambda x: str(x) + ' b/w 1 & 2', listwords))
title.extend(map(lambda x: str(x) + ' before 1', listwords))
title.extend(map(lambda x: str(x) + ' after 2', listwords))
title.extend(map(lambda x: str(x) + ' (noun) b/w 1 & 2', listwords))
title.extend(map(lambda x: str(x) + ' (verb) b/w 1 & 2', listwords))
title.append('interaction b/w 1 & 2')

def wordvector(words):
	lwordvector = [0] * len(listwords)
	words = words.replace('"', '')
	if len(words) > 0:
		lwords = words.split('|')
		#print lwords
		for word in lwords:
			lwordvector[dictwords[word]] = 1
	return lwordvector

selectedattr = [1, 2, 3, 4, 5, 6]
selectedattr.extend([264,311,381,449,466,476,496,616,761,818,906,963,979,1126,1146,1165,1179,1210,1244,1277,1290,1401,1546,1570,1616,1665,1778,1802,2067,2154,2247,2384,2401,2429,2442,2476,2481,2482,2858,2877,2936,2972,2992,3040,3108,3114,3155,3195,3284,3425,3429,3434,3443,3469,3503,3516,3546,3579,3722,3739,3798,3962,3997,4699,4839,5013])
#selectedattr.extend([34,103,154,158,215,249,394,421,428,430,448,540,585,590,650,654,672,704,748,751,781,797,843,854,964,980,1102,1185,1211,1216,1220,1278,1322,1377,1441,1447,1531,1557,1594,1790,1791,1798,2001,2026,2170,2207,2317,2326,2402,2444,2508,2613,2758,2819,3056,3104,3110,3175,3272,3322,3326,3376,3513,3616,3664,3918,3936,3993,4093,4115,4225,4315,4672,4730,4792,4868,4934,5147])
selectedattr.append(6686)
selectedattr = [x - 1 for x in selectedattr] # correcting off by one error

def writerow(g, l, d, selectedonly=False):
	if not selectedonly:
		for i in range(0, len(l) - 1):
			g.write(str(l[i]) + d)
		g.write(str(l[-1]) + '\n')
	else:
		for i in range(0, len(selectedattr) - 1):
			g.write(str(l[selectedattr[i]]) + d)
		g.write(str(l[selectedattr[-1]]) + '\n')

f = open("basicFeatures_200.csv")
#f = open("basicFeatures.csv")
g = open("/tmp/featurevector.csv", 'w')
writerow(g, title, ',', False)
lbf = []
for line in f:
	lresult = []
	lbf = line.strip().split(delim)
	lresult.extend(map(lambda x: '"' + x + '"', lbf[1:5]))
	lresult.append(lbf[5])
	lresult.extend(wordvector(lbf[6]))
	lresult.extend(wordvector(lbf[7]))
	lresult.extend(wordvector(lbf[8]))
	lresult.extend(wordvector(lbf[9]))
	lresult.extend(wordvector(lbf[10]))
	lresult.append(lbf[11])
	writerow(g, lresult, ',', False)
	assert(len(lresult) == len(title))
