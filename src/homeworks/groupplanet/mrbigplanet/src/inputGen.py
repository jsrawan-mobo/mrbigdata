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

def readFormattedData (fileName, delimiterIn):
    rowData = []
    with open(fileName, 'rb') as f:
        reader = csv.reader(f, delimiter = delimiterIn, quoting=csv.QUOTE_NONE )
        for row in reader:
            rowData.append( row ) 
    return rowData;
    

def aggregateDataForBDD(dataObs, userInfo, itemInfo):
    # This takes the set of data and aggregrates relevant data sources
    # Reads in the files and appends
    
    dataBDD = []
    
    # Output
    # obs.Id, obs.timestamp,  user.Age, user.gender, user.occupation, user.zip,  item.movieType, 
    for dataRecord in dataObs:
        
        
        
        userId = dataRecord[0]
        itemId = dataRecord[1]
        rating = dataRecord[2]
        timestamp = dataRecord[3]
        
        
        iU = userInfo.index(userId)
        iI = itemInfo.index(itemId)
        
        recordBDD = []
        recordBDD[0] = userId
        recordBDD[1] = timestamp
        recordBDD[1] = userInfo[iU][1] #age
        recordBDD[2] = userInfo[iU][2] #gender
        recordBDD[3] = userInfo[iU][3] #occupation
        recordBDD[4] = userInfo[iU][4] #zip
        recordBDD[5] = 0;
        
        for j in range(18) :        
            recordBDD[5] += itemInfo[iI][7+j] * 2^j 
            
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
    dataObs = readFormattedData(userDataFilePath, delimiter)
     
    #2.  Do selection of data
    numPts = 1000
    dataSelect = selectData(dataObs, numPts)   
                    
        
    #3.  Aggregate the data from relevant files
    userDataFilePath = './data/100K/ml-data/u.user'
    delimiter = '|'
    userInfo = readFormattedData(userDataFilePath, delimiter)
    
    userDataFilePath = './data/100K/ml-data/u.item'
    delimiter = '|'
    itemInfo = readFormattedData(userDataFilePath, delimiter)
    
    dataBDD = aggregateDataForBDD(dataSelect, userInfo, itemInfo);
    
    
    #4.  Normalize various fields
    
    #5.  Write to json.
    
    #first run the initializer to get starting centroids
    
    fileOut=open('./data/observation.json',"w") 
    outString = json.dumps( dataBDD )
    fileOut.write(outString)
                

if __name__ == '__main__':
    main()