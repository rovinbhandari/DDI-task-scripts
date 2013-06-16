#!/usr/bin/python
# Author : Rajat Khanduja
# 
# Extracts features from the files in the directory.
#
# Usage :-
#   python extractFeatures.py <directory_path> <dictionary_file>
#
# Features extracted (in the order they will be printed)
# 0. ID
# 1. Drug1 (in the pair)
# 2. Drug2 (in the pair)
# 3. Head word of drug1
# 4. Head word of drug2
# 5. Number of words between two drugs}
# 6. Unique words between two drugs   }
# 7. Unique words before drug1        } - based on the words obtained separately
# 8. Unique words after  drug2        }
# 9. Nouns between two drugs
#10. Verbs between two drugs
#11. Interaction between two drugs



import os
import xml.etree.ElementTree as ET
import nltk 

STOPWORDS = nltk.corpus.stopwords.words("english")
STEMMER   = nltk.PorterStemmer()
NEIGHBOUR_DISTANCE = 3

def extractFeaturesForPair(pairRef, sentenceRef, entity1Ref, entity2Ref,
                           dictionary):
  '''
  Function that extracts features for every pair given the entities involved
  and the parent sentence and returns it as a dictionary
  '''
  
  features = {}
  sentence = sentenceRef.attrib['text']

  # POS tag for the sentence
  taggedSentence = nltk.pos_tag(sentence.split())
  
  # Get names of drugs.
  features['drug1'] = entity1Ref.attrib['text']
  features['drug2'] = entity2Ref.attrib['text']

  # Head words of the drugs.
  features['head1'] = features['drug1'].split()[0]
  features['head2'] = features['drug2'].split()[0]

  # Distance between drug names (ignoring stopwords), words between drugs
  # and words before and after the drugs.
  limitsDrug1 = map (lambda x: x.split("-"), entity1Ref.attrib['charOffset'].split(";"))
  limitsDrug2 = map (lambda x: x.split("-"), entity2Ref.attrib['charOffset'].split(';'))
  textBetweenDrugs = ""
  neighboursBeforeDrug1 = filter(lambda x: x in dictionary,
                        map(lambda x: STEMMER.stem(x),
                          sentence[:int(limitsDrug1[0][0])].strip().split()))[:NEIGHBOUR_DISTANCE]
  neighboursAfterDrug2 = filter(lambda x: x in dictionary, 
                        map(lambda x: STEMMER.stem(x),
                          sentence[int(limitsDrug2[-1][1]):].strip().split()))[:NEIGHBOUR_DISTANCE]

  # Get all words before each of the drugs to get the word-position of the drugs
  # (required to find the nouns and verbs between the two drug names)
  nWordsBeforeDrug1 = len(sentence[:int(limitsDrug1[0][0])].strip().split())
  
  nWordsBeforeDrug2 = len(sentence[:int(limitsDrug2[0][0])].strip().split())

  nounsBetweenDrugs = []
  verbsBetweenDrugs = []

  if int(limitsDrug1[-1][1]) < int(limitsDrug2[0][0]):
    textBetweenDrugs = sentence[int(limitsDrug1[-1][1]) + 1: int(limitsDrug2[0][0])].strip()  
    nounsBetweenDrugs = filter(lambda x: x in dictionary,
                          map(lambda x: STEMMER.stem(x[0]),
                            filter(lambda x: x[1].startswith('NN'), 
                              taggedSentence[nWordsBeforeDrug1 + 1 : nWordsBeforeDrug2])))
    verbsBetweenDrugs = filter (lambda x: x in dictionary,  
                          map(lambda x: x[0],
                            filter(lambda x: x[1].startswith('VB') and x[1] in dictionary, 
                              taggedSentence[nWordsBeforeDrug1 + 1 : nWordsBeforeDrug2])))

  features['neighboursBeforeDrug1'] = neighboursBeforeDrug1
  features['neighboursAfterDrug2'] = neighboursAfterDrug2

  wordsBetweenDrugs = filter(lambda x: 
                            x not in STOPWORDS, textBetweenDrugs.split())
  features['distanceBetweenDrugs'] = len(wordsBetweenDrugs)
  features['wordsBetweenDrugs'] = filter(lambda x: x in dictionary,
                                    map(lambda x: STEMMER.stem(x), 
                                        wordsBetweenDrugs))  

  # Add the nouns and the number of nouns
  features['nounsBetweenDrugs'] = nounsBetweenDrugs
  features['numberOfNouns'] = len(nounsBetweenDrugs)

  # Add the verbs and the number of verbs
  features['verbsBetweenDrugs'] = verbsBetweenDrugs
  features['numberOfVerbs'] = len(verbsBetweenDrugs)
  
  # Relation exists or not
  features['ddi'] = pairRef.attrib['ddi']
  
  return features

  
def processFile(filename, dictionary):
  root = ET.parse(filename).getroot()
  features = dict()
  for sentence in root:
    entities = []
    for child in sentence:
      if child.tag == "entity":
        entities.append(child)
      if child.tag == "pair":
        entity1 = filter(lambda x: x.attrib['id'] == child.attrib['e1'], 
                          entities)[0]

        entity2 = filter(lambda x: x.attrib['id'] == child.attrib['e2'], 
                          entities)[0]
        
        features[child.attrib['id']] = extractFeaturesForPair(child, sentence, 
                                                              entity1, entity2,
                                                              dictionary)
  return features                                                              

def processDir (directory, dictionary):
  features = dict()
  for (path, dirs, files) in os.walk(directory):
    for f in files:
      features.update(processFile(os.path.join(path, f), dictionary))
  return features

if __name__ == "__main__":
  import sys
  directory = sys.argv[1]
  dictionary = map(lambda x: x.strip(), open(sys.argv[2]).readlines())
  features = processDir(directory, dictionary)
  delimiter = ",;,"
  for pair in features:
    entry = pair 
    entry += delimiter + features[pair]['drug1']
    entry += delimiter + features[pair]['drug2']
    entry += delimiter + features[pair]['head1']
    entry += delimiter + features[pair]['head2']
    entry += delimiter + str(features[pair]['distanceBetweenDrugs'])
    entry += delimiter + '"' + "|".join(features[pair]['wordsBetweenDrugs']) + '"'
    entry += delimiter + '"' + "|".join(features[pair]['neighboursBeforeDrug1']) + '"'
    entry += delimiter + '"' + "|".join(features[pair]['neighboursAfterDrug2']) + '"'
    entry += delimiter + '"' + "|".join(features[pair]['nounsBetweenDrugs']) + '"'
    entry += delimiter + '"' + "|".join(features[pair]['verbsBetweenDrugs']) + '"'
    entry += delimiter + features[pair]['ddi']
    print entry
