#!/usr/bin/python
# Author : Rajat Khanduja
# Date : 17/3/13
#
# This file contains functions to read xml files in a directory and returns a  
# set of the names of drugs in those files.

import os
import xml.etree.ElementTree as ET

def extractDrugNamesFromXmlTree(documentRoot):
  '''
  Function that returns the names of the drugs that occur in a document
  given the documentRoot of the xml file. 
  '''
  drugNames = set()
  for sentence in documentRoot:
    for child in sentence:
      if child.tag == "entity":
        drugNames.add(child.attrib['text'])
  
  return drugNames

def extractDrugNamesFromDir(directoryPath):
  '''
  Function that returns a set of drug names that occur in documents in a 
  particular directory in the required XML format.
  '''
  return reduce(lambda x,y: x.union(
                  extractDrugNamesFromXmlTree(ET.parse(y).getroot())), 
          map(lambda x: os.path.join(directoryPath, x), 
            filter(lambda x: x.endswith(".xml"), 
              os.listdir(directoryPath))), set())
 
if __name__ == '__main__':
  import sys
  directories = sys.argv[1:]
  drugNames = reduce(lambda x,y: x.union(extractDrugNamesFromDir(y)), 
                        directories, set())
  for drug in drugNames:
    print drug
