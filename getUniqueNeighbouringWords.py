#!/usr/bin/python
# Author : Rajat Khanduja
# This program creates a list of unique non-stop words that occur in the 
# neighbourhood of the entity names. 
#
# Usage :
# python getUniqueNeighbouringWords.py <director> <neighbourhood>

import sys
import pprint
import os
import nltk
import xml.etree.ElementTree as ET

STOPWORDS = nltk.corpus.stopwords.words("english")
STEMMER   = nltk.PorterStemmer()

def neighbours(sentenceRef, entityRef, neighbourhoodDistance, entities):
  sentence = sentenceRef.attrib['text'].lower()
  entityLimits = map(lambda x: x.split("-"), entityRef.attrib['charOffset'].split(';'))
#  print entityLimits
  wordsBefore = sentence[:int(entityLimits[0][0])].strip().split()
  wordsAfter  =  sentence[int(entityLimits[-1][1]) + 1:].strip().split()

  # Remove stopwords and take only neighbourhoodDistance words
  wordsBefore = filter(lambda x: x not in STOPWORDS and x.isalnum(), 
                        wordsBefore[-neighbourhoodDistance:])
  wordsAfter  = filter(lambda x: x not in STOPWORDS and x.isalnum(), 
                        wordsAfter[:neighbourhoodDistance])

  words = []
  for word in wordsBefore:
    if word not in entities:
      word = STEMMER.stem(word)
    words.append(word)
  for word in wordsAfter:
    if word not in entities:
      word = STEMMER.stem(word)
    words.append(word)
#  print words
  return words

def processFileForNeighbours(filename, neighbourhoodDistance):
#  print filename
  xmlRoot = ET.parse(filename).getroot()
  words = []
  entitiesList = []
  for sentence in xmlRoot:
    for child in sentence:
      if child.tag == "entity":
        entitiesList.append(child.attrib["text"].lower())
  for sentence in xmlRoot:
    for child in sentence:
      if child.tag == "entity":
#        print filename
        wordsInSentence = neighbours(sentence, child, neighbourhoodDistance,
                                     entitiesList)
        for word in wordsInSentence:
#          print word
          words.append(word)

  wordCount = dict()
  for word in words:
    if word in wordCount:
      wordCount[word] += 1
    else:
      wordCount[word]  = 1
  
  return wordCount

def processDirForNeighbours(directory, neighbourhoodDistance):
  
  neighbours = dict() 
  for (path,dirs,files) in os.walk(directory):
    for f in files:
      if f.endswith(".xml"):
        neighbours_f = processFileForNeighbours(os.path.join(path, f), neighbourhoodDistance)

      for n in neighbours_f:
        if n in neighbours:
          neighbours[n] += neighbours_f[n]
        else:
          neighbours[n] = neighbours_f[n]

  return neighbours    

if __name__ == "__main__":
  directory = sys.argv[1]
  neighbourhood = int(sys.argv[2])
  neighbours = processDirForNeighbours(directory, neighbourhood)
  frequency_threshold = 5  
  frequent_neighbours = filter (lambda x: neighbours[x] >= frequency_threshold, 
                        neighbours)
  for neighbour in frequent_neighbours:
    print neighbour
#  print sorted(neighbours.iteritems(), key=lambda item: -item[1])
#  print len(neighbours)
