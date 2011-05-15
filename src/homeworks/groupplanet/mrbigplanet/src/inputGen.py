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

def splitData(userData):
    #This takes the userData, and formats it (i.e. removes tabs).
    return 1;

def aggregateData(reader):
    # This takes the set of data and aggregrates relevant data sources
    return 1;
   
   
def selectData(rowData, numPoints):
    #This selects n randomly selected points from the data set for use as a training set.
    
    #rowData = []
    #for row in reader:
    #    rowData.append(row) 
        
    indexList = sample(range(len(rowData)), numPoints)    
    dataObs = []       
    for i in indexList:
        dataObs.append(rowData[i])
            
    return dataObs;   
    
    
def getlatLongFromZip (zip):
    #This gets the lat lon from the zip file.
    return 1;    

def main():
    
    #1.  Load the u.dat file into memory
    rowData = []
    userDataFilePath = '/home/jsrawan/dev/mlearn/mrbigdata-jsrawan-git/src/homeworks/groupplanet/mrbigplanet/src/data/100K/ml-data/u.data'
    with open(userDataFilePath, 'rb') as f:
        reader = csv.reader(f, delimiter = '\t', quoting=csv.QUOTE_NONE )
        for row in reader:
            rowData.append( row ) 
            #print rowData[ len[rowData] - 1]               
      
    
        
    fileOut=open('/home/jsrawan/dev/mlearn/mrbigdata-jsrawan-git/src/homeworks/groupplanet/mrbigplanet/src/data/observation.json',"w") 
    outString = json.dumps( rowData )
    fileOut.write(outString)
            
    numPts = 1000;
    dataObs = selectData(reader, numPts)   
    print (dataObs)
                    
    #2.  Do selection of data
        
    #3.  Aggregate the data from relevant files
    
    #4.  Normalize various fields
    
    #5.  Write to json.
    
    #first run the initializer to get starting centroids
    

if __name__ == '__main__':
    main()