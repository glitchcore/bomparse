# -*- coding: utf-8 -*-
"""
Spyder Editor

This temporary script file is located here:
/home/anper/.spyder2/.temp.py
"""

from random import random
from math import *
import scipy.signal as sp
import numpy as np

import csv
import re
import time
import argparse
from collections import namedtuple

argparser = argparse.ArgumentParser(description='Process P-CAD BOM files')

argparser.add_argument('filename', type=str, help='filename')

args = argparser.parse_args()

print "filename: ", args.filename

def attributesParse(attributeList, data):
    attributesIdx = {}
    
    for attribute in attributeList:
        attributesIdx[attribute] = data.index(attribute)
        
    def parser (rowData):
        row = {}
        for idx in attributesIdx:
            row[idx] = rowData[attributesIdx[idx]]
        return row
        
    return parser

def refIdx(string):
    return int(re.sub('[A-Z]', '', string))
    
def refZip (refs):
    zippedRef = []
    if(len(refs) > 0):
        zippedRef.append(refs[0]) # append first element
        for i, ref in enumerate(refs[1:-1]):
            if (refIdx(refs[i+1]) == refIdx(refs[i]) + 1) and (refIdx(refs[i+1]) == refIdx(refs[i+2]) - 1):
                if(zippedRef[-1] != ".."):
                    zippedRef.append("..")
            else:
                zippedRef.append(ref)
        if(len(refs) > 1):
            zippedRef.append(refs[-1]) # append last element
    
    for i, ref in enumerate(zippedRef):
        if ref == "..":
            zippedRef[i-1] = zippedRef[i-1] + ".." + zippedRef[i+1]
            del(zippedRef[i])
            del(zippedRef[i])
            
    return zippedRef
        

with open(args.filename, 'rb') as bomFile:
    bomCSV = csv.reader(bomFile, delimiter=',', quotechar='\"')
    
    header = bomCSV.next()
    print "header: ", header
    print 
    attributes = ['Count', 'ComponentName', 
                  'RefDes', 'PatternName', 
                  'Value', 'STATUS', 'Part Number', 
                  'Voltage']
    attributesParser = attributesParse(attributes, header)
    
    components = []
    component = {}
    prevName = ""
    
    for row in bomCSV:
        if(len(row) != 0):
            row = attributesParser(row)
            # print row
            
            #skip non-placed components
            if row["STATUS"] == "DNP" or row["Value"] == "NC":
                continue
            
            if(row["Part Number"] != ""):
                name = row["Part Number"]
            else:
                prefix = ""
                if(row["RefDes"][0] == "C"):
                    prefix = u"Конденсатор"
                if(row["RefDes"][0] == "R"):
                    prefix = u"Резистор"
                name = prefix + " " + row["ComponentName"] + " " + \
                row["Value"] +  " " + row["Voltage"]
                    
            #add new component
            if(prevName.upper() != name.upper()):
                # save prev component if exist
                if(len(component) != 0):
                    component["refs"] = refZip(component["refs"])
                    components.append(component)
                
                component = {}
                component["Count"] = 0
                component["refs"] = []
                
                component["name"] = name
                prevName = name
                # print "component: ", component
                
            refDes = row["RefDes"]
            component["Count"] += 1
            component["refs"].append(refDes)
            
            
    #add last component to array
    if(len(component) != 0):
        component["refs"] = refZip(component["refs"])
        components.append(component)
    # print components
    
    width = 3
    rangeWidth = 2
    
    outputList = []
    outputRow = {}
    rowSize = 0
    
    print '"Поз.обозн.","Наименование","Кол-во","Примечание"'
    for component in components:
        # print component["Count"], " ", component["name"]
        outputRow["Count"] = component["Count"]
        outputRow["name"] = component["name"]
        outputRow["refs"] = ""
        
        for i, ref in enumerate(component["refs"]):
            if(rowSize > 0):
                outputRow["refs"] += ", "
            outputRow["refs"] += ref
            if(ref.find("..") == -1):
                rowSize += 1
            else:
                rowSize += rangeWidth
                
            if(rowSize >= width) or (i == len(component["refs"]) - 1):
                print '"',outputRow["refs"],'","',outputRow["name"],'","',outputRow["Count"],'",""'
                outputList.append(outputRow)
                rowSize = 0
                outputRow["Count"] = ""
                outputRow["name"] = ""
                outputRow["refs"] = ""
    


