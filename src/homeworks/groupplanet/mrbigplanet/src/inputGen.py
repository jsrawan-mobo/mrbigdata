#  tar xvzf ml-data.tar__0.gz
#  cd ml-data/
#  modify /usr/bin/perl in allbut.pl
#  modify ./allbut in mku.sh
#  mku.sh

'''
Created on May 15, 2011

@author: jag-srawan
'''
import json
from math import sqrt
from numpy import random
from random import sample
from random import seed
from operator import itemgetter


import csv

'''
Loads the movie lends 100K data
Outputs a data set randomly selected with replacement in json format
To be used in binary decision tree.
The rating is good.
Can be read in by tree predict.

fields = userId,movieType,age,gender,occupation,zip,timestamp,rating
type =  nominal,ordinal, interval, nominal, ordinal, nominal, interval, interval.
 
'''

def collect(l, index):
    #this returns a map that can be used to call index on.
   return map(itemgetter(index), l)


def readFormattedDataAsMap (fileName, delimiterIn, mapI = 0):
    # This reads in as array, but assign an index to one of the map value
    # so it is an array of  [a, data[a,b,c,d,e] ]
    rowData = []
    with open(fileName, 'rb') as f:
        reader = csv.reader(f, delimiter = delimiterIn, quoting=csv.QUOTE_NONE )
        for row in reader:
            
            newRow = [ row[mapI], row]
            rowData.append( newRow ) 
    return rowData;
    

def aggregateDataForBDD(dataObs, userInfo, itemInfo):
    # This takes the set of data and aggregrates relevant data sources
    # Reads in the files and appends
    
    dataBDD = []
    
    # Output
    # obs.Id, obs.timestamp,  user.Age, user.gender, user.occupation, user.zip,  item.movieType, 
    for dataRecord in dataObs:
        
        
        
        userId = dataRecord[1][0]
        itemId = dataRecord[1][1]
        rating = dataRecord[1][2]
        timestamp = dataRecord[1][3]
        
        iU = collect(userInfo,0).index(userId)   # = 1
        iI = collect(itemInfo,0).index(itemId)   # = 1

        #iU = [for y in userInfo].index(1,0)
        #iI = itemInfo.index(itemId)
        
        recordBDD = []
        recordBDD.insert(0, long ( userId)  )
        recordBDD.insert(1, long ( timestamp ) )
        recordBDD.insert(2, long ( userInfo[iU][1][1] ) )#age
        recordBDD.insert(3, userInfo[iU][1][2] )#gender
        recordBDD.insert(4, userInfo[iU][1][3] )#occupation
        recordBDD.insert(5, userInfo[iU][1][4]  )#zip, note postal codes are included.
        recordBDD.insert(6, long (0) ) #movie
        recordBDD.insert(7, float ( rating) ) #rating
        
        for j in range(18) :        
            recordBDD[6] += long ( itemInfo[iI][1][5+j] ) * pow(2,j) 
            
        dataBDD.append(recordBDD)
        
    
    
    return dataBDD;
   
   
def selectData(obsData, numPoints):
    #This selects n randomly selected points from the data set for use as a training set.
    
    #rowData = []
    #for row in reader:
    #    rowData.append(row) 
        
    indexList = sample(range(len(obsData)), numPoints)    
    selectedObs = []       
    for i in indexList:
        selectedObs.append(obsData[i])
            
    return selectedObs;   
    
    
def getlatLongFromZip (zip):
    #This gets the lat lon from the zip file.
    return 1;    

def main():
    
    
    #1. Read main observations.
    userDataFilePath = './data/100K/ml-data/u.data'
    delimiter = '\t'
    dataObs = readFormattedDataAsMap(userDataFilePath, delimiter)
     
    #2.  Do selection of data
    numPts = 1000
    dataSelect = selectData(dataObs, numPts)   
                    
        
    #3.  Aggregate the data from relevant files
    userDataFilePath = './data/100K/ml-data/u.user'
    delimiter = '|'
    userInfo = readFormattedDataAsMap(userDataFilePath, delimiter)
    
    userDataFilePath = './data/100K/ml-data/u.item'
    delimiter = '|'
    itemInfo = readFormattedDataAsMap(userDataFilePath, delimiter)
    
    dataBDD = aggregateDataForBDD(dataSelect, userInfo, itemInfo);
    
    
    #4.  Normalize various fields
    
    #5.  Write to json.
    
    #first run the initializer to get starting centroids
    
    fileOut=open('./data/observation.json',"w") 
    outString = json.dumps( dataBDD )
    fileOut.write(outString)
                

if __name__ == '__main__':
    main()