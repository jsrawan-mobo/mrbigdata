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
def getChildNodeId (nodeId, isLtree = True):
    depth = getDepthFromId(nodeId)
    firstNodeAtPrev = math.pow(2,depth)
    
    childNodeId = math.pow(2,depth+1) +  (nodeId - firstNodeAtPrev ) * 2
    
    if (not isLtree):
        childNodeId += 1
     
    return int ( childNodeId ) 

# Depth = 0 is the root node
def getDepthFromId (nodeId):
        depth = int ( math.floor( math.log( nodeId,2) ) )
        return depth
    
# Depth = 0 is the root node
def enumerateIdsFromDepth (depth):
    
        firstNodeId = int ( math.pow(2,depth) )
        numNodes = int ( math.pow(2,depth) )
        
        idRange =  range (firstNodeId , firstNodeId + numNodes, 1)
        
        return idRange    
    
    
#    
def divideset(rows,column,value):
        # Make a function that tells us if a row is in
        # the first group (true) or the second group (false)
        split_function=None
        if isinstance(value,int) or isinstance(value,float):
            split_function=lambda row:row[column]>=value  #note larger than equal to for left node.
        else:
            split_function=lambda row:row[column]==value
        # Divide the rows into two sets and return them
        set1=[row for row in rows if split_function(row)]
        set2=[row for row in rows if not split_function(row)]
        return (set1,set2)
        
def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False    
            
    
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
        with open(self._fileName, 'rwb') as f:
            reader = csv.reader(f, delimiter = self._delimiter, quoting=csv.QUOTE_NONE )
            for row in reader:
                
                newRow = [ int(row[0]), [ int( row[0]), int(row[1]), row[2], int(row[3]) ]]
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
        dataRow = self._rowData[rowId][1]
        return [ int ( dataRow[0] ), int ( dataRow[1] ), dataRow[2], ]

     
    def appendData (self, nodeId, colNum, splitPredicate, count):
        self._rowData.append( [nodeId, [ nodeId, colNum,splitPredicate, count ] ] )
        
    def updateData (self, nodeId, colNum, splitPredicate, count):
        
        try:
            rowId = collect(self._rowData,0).index(nodeId)   # = 1
        except ValueError:
                print "could not find node Id: " + str(nodeId)
        
        orginalData = self._rowData[rowId]
        self._rowData[rowId] = [nodeId,[ nodeId, colNum,splitPredicate, count]]
         
    #reads the file into csv
    # Node_id, colNumber, splitPredicate,
    # returns the nodeId of the new node      
    def addPredicate(self, parentId, colNumber, splitPredicate, count):
        
        lNodeId = getChildNodeId(parentId, True)
        rNodeId = getChildNodeId(parentId, False)
  
        self.updateData(parentId, colNumber, splitPredicate, count )
        
        if (colNumber != -1): #don't add leaf nodes.
            self.appendData( lNodeId, -1,-1, -1 )
            self.appendData( rNodeId, -1,-1, -1 )
        
        
    
    #Gets the depth of the tree      
    #Simply get the max of tree  
    def getDepth (self):
            sortedMapKeys = collect(self._rowData,0).sort()
            
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
        ids = enumerateIdsFromDepth(depth)
        idsMap = collect(self._rowData, 0)
        
        nodeIds = []
        for id in ids:
            idsIndex = -1 
            try:
                idsIndex = idsMap.index( id )
            except ValueError:
                #do nothing, this is expected time to time
                print ''
                
            if ( idsIndex >= 0 ):
                nodeIds.append(id)                                
            
        return nodeIds
    
    def getNodeIdToRoot(self,nodeId):
    
        selfDepth = getDepthFromId(nodeId)
        parentDepth = selfDepth - 1
        firstNodeAtCurrent = int ( math.pow(2,selfDepth) )
        
        parentNodeId = int ( math.pow(2,parentDepth) +  int ( (nodeId - firstNodeAtCurrent ) / 2 ) )
        
        if ( parentNodeId != 1): 
            returnedList = self.getNodeIdToRoot(parentNodeId)
            returnedList.append(parentNodeId)
            return returnedList
        else: # root
            return [ parentNodeId ];
        
    def getApplicableInputsforNodeId(self, nodeId, inputs):
        
        #1 Figure out he node Id order
        
        idList = self.getNodeIdToRoot(nodeId)
        idList.append(nodeId) #for the foreloops, this is required.
        currentSet = inputs
        
        #Just go through each node, and see what data is applicable.
        for i in range (len( idList) - 1):
                 
            id = idList[i];
            nextId = idList[i+1]; 
            nodeInstruction = self.getDataRowById(id) 
            
            column = nodeInstruction[1]
            decisionStr = nodeInstruction[2]
            decision=''
            
            if ( is_float(decisionStr) ) :
                if ( is_int(decisionStr) ):
                    decision = int(decisionStr)
                else:
                    decision = float(decisionStr)
            else:
                decision = decisionStr
                
            (set1, set2) = divideset( currentSet, column, decision )   
                
            if ( nextId % 2 ) == 0:
                currentSet = set1
            else:
                currentSet = set2
        
        return currentSet 
    
    
    def doMagic (self, someNumber):
        
        return self.magicNumber + someNumber + self.someVar       
    
        