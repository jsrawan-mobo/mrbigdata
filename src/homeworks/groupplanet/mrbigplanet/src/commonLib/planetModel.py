#!/usr/bin/python
# Filename: planetModel.py

'''
Created on May 19, 2011

@author: jsrawan
'''


import json
import re
import string
import math
from math import sqrt
from numpy import random
from random import sample
from random import seed
from operator import itemgetter
import csv


def collect(l, index):
    #this returns a map that can be used to call index on.
    #itemgetter returns the index'ed item in list l.  Then we cast to maop
    # we could cast to other things as requried.
    # call this like collect(l,0).mapFunction();
        return map( itemgetter(index), l)


# This returns a nodeId,that can be derived by the depth of the tree.
# rTree = lTree +1    
def getChildNodeId (nodeId, isLtree = False):
    depth = getDepthFromId(nodeId)
    firstNodeAtPrev = math.pow(2,depth)
    
    childNodeId = math.pow(2,depth+1) +  (nodeId - firstNodeAtPrev ) * 2
    
    if (not isLtree):
        childNodeId += 1
     
    return int ( childNodeId ) 

# Depth = 0 is the root node
def getDepthFromId (nodeId):
        depth = math.floor( math.log(nodeId,2) )
        return depth
    
# Depth = 0 is the root node
def getIdsFromDepth (depth):
    
        firstNodeId = math.pow(2,depth)
        numNodes = math.pow(2,depth)
        
        idRange =  range (firstNodeId , depth + numNodes, 1)
        
        return idRange    
    
    
class planetModel(object):

    _fileName = ''
    someVar = 0
    _rowData = []
    _delimiter = ','
    _arrayDelimiterIn = ','
    '''
    classdocs
    '''

    def __init__(self, fileName):
        '''
        Like Perl except we don't have to do anything
        '''
        self._fileName = fileName
        
        

    def readFile (self):
        rowData = []
        with open(self._fileName, 'rb') as f:
            reader = csv.reader(f, delimiter = self._delimiter, quoting=csv.QUOTE_NONE )
            for row in reader:
                
                newRow = [ row[0], row]
                rowData.append( newRow ) 
        f.close()
        self._rowData = rowData        
     
    #Write the current in-memory nodes to file      
    def flushFile (self):
        
        with open(self._fileName, 'wb') as f:
            writer = csv.writer(f, delimiter = self._delimiter, quoting=csv.QUOTE_NONE )
        
            for row in self._rowData:
                data = row[1]
                writer.writerow(data)
        f.close()
     
     
    def getDataRowById(self, nodeId):
        rowId = collect(self._rowData,0).index(nodeId)   # = 1
        return self._rowData[rowId][1]

     
    def appendData (self, nodeId, colNum, splitPredicate):
        self._rowData.append( [nodeId, [ nodeId, -1,-1 ] ] )
        
    def updateData (self, nodeId, colNum, splitPredicate):
        
        rowId = collect(self._rowData,0).index(nodeId)   # = 1
        
        orginalData = self._rowData[rowId]
        self._rowData[rowId] = [nodeId,[ nodeId,colNum,splitPredicate]]
         
    #reads the file into csv
    # Node_id, colNumber, splitPredicate,
    # returns the nodeId of the new node      
    def addNodes(self, parentId, colNumber, splitPredicate):
        
        lNodeId = getChildNodeId(parentId, False)
        rNodeId = getChildNodeId(parentId, True)
  
        self.updateData(parentId, colNumber, splitPredicate )
        
        self.appendData( lNodeId, -1,-1 )
        self.appendData( rNodeId, -1,-1 )
        
        
    
    #Gets the depth of the tree      
    #Simply get the max of tree  
    def getDepthFromId (self):
            sortedMapKeys = collect(self._rowData,0).sort
            
            last = len(sortedMapKeys)
            maxNodeI =  sortedMapKeys.index(last)
            rowData = self._rowData[maxNodeI][1]
            nodeId = rowData[0]
            depth = getDepthFromId(nodeId)
            return depth                     
        
    #returns the node id's at the tree
    # Simply get all possible nodes at depth
    # Return the node ids        
    def getNodeIdsAtDepth(self, depth):
        ids = getIdsFromDepth
        idsMap = collect(self._rowData,0)
        
        nodeIds = []
        for id in ids:
            if ( idsMap.index(id) >= 0) :
                nodeIds.append(id)
            
        return nodeIds
        
        
    def doMagic (self, someNumber):
        
        return self.magicNumber + someNumber + self.someVar       
    
        