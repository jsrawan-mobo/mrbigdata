


from optparse import OptionParser
import json
import math


from commonLib import planetModel


my_data =[['slashdot','USA','yes',18,0],
        ['google','France','yes',23,1],
        ['digg','USA','yes',24,1],
        ['kiwitobes','France','yes',23,1],
        ['google','UK','no',21,1],
        ['(direct)','New Zealand','no',12,0],
        ['(direct)','UK','no',21,1],
        ['google','USA','no',24,1],
        ['slashdot','France','yes',19,0],
        ['digg','USA','no',18,0],
        ['google','UK','no',18,0],
        ['kiwitobes','UK','no',19,0],
        ['digg','New Zealand','yes',12,1],
        ['slashdot','UK','no',21,0],
        ['google','UK','yes',18,1],
        ['kiwitobes','France','yes',19,1]]

my_data_orig=[['slashdot','USA','yes',18,'None'],
        ['google','France','yes',23,'Premium'],
        ['digg','USA','yes',24,'Basic'],
        ['kiwitobes','France','yes',23,'Basic'],
        ['google','UK','no',21,'Premium'],
        ['(direct)','New Zealand','no',12,'None'],
        ['(direct)','UK','no',21,'Basic'],
        ['google','USA','no',24,'Premium'],
        ['slashdot','France','yes',19,'None'],
        ['digg','USA','no',18,'None'],
        ['google','UK','no',18,'None'],
        ['kiwitobes','UK','no',19,'None'],
        ['digg','New Zealand','yes',12,'Basic'],
        ['slashdot','UK','no',21,'None'],
        ['google','UK','yes',18,'Basic'],
        ['kiwitobes','France','yes',19,'Basic']]

# This class is just to hold the decision nodes, which decide the col, splitValue, results=labels for leaf nodes, and true/false branch is the number of nodes for each 
# branch label.
class ModelNode:
    def __init__(self, id = None, col=-1, split=None, count = None):
        self.col=col
        self.split=split
        self.id=id
        self.count=count
        
        
class decisionnode:
    def __init__(self, id = None, col=-1,value=None,results=None,tb=None,fb=None, ):
        self.col=col
        self.value=value
        self.results=results
        self.tb=tb
        self.fb=fb
        self.id=id        

        
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
    
# Create counts of possible results (the last column of
# each row is the result)
# Takes the class label, and does a count(label)
# Return is a list of counts for each output label.
# i.e. label1=10, label2=10
def uniquecounts(rows):
    results={}
    for row in rows:
    # The result is the last column
        r=row[len(row)-1]
        if r not in results: results[r]=0
        results[r]+=1
    return results
    
    
# Probability that a randomly placed item will
# be in the wrong category
# This code is super wierd, instead of 1- sum-square impurities
# It does dot product instead, but the numbers come out the same.
def giniimpurity(rows):
    total=len(rows)
    counts=uniquecounts(rows)
    imp=0
    for k1 in counts:
        p= math.pow((float(counts[k1])/total),2)
        imp+=p
    imp = 1- imp
    return imp

# Entropy is the sum of p(x)log(p(x)) across all
# the different possible results
def entropy(rows):
    from math import log
    log2=lambda x:log(x)/log(2)
    results=uniquecounts(rows)
    # Now calculate the entropy
    ent=0.0
    for r in results.keys( ):
        p=float(results[r])/len(rows)
        ent=ent-p*log2(p)
    return ent

# Perform variance on class lables for the given node
# BestSplit = D * Var(D) -Dl*Var(Dl) + Dr+Var(Dr))
# This is when output is numerical
def splitVariance(parentRows, childL, childR):
    
    
    magD = magnitude (parentRows )
    magDl = magnitude (childL)
    magDr = magnitude (childR )
    varD  = variance(parentRows)
    varDl = variance(childL)
    varDr = variance(childR)
    
    
    splitVar = magD * varD - ( magDl * varDl + magDr * varDr )
    
    return splitVar
    
    
    
# Take the last column and 
def magnitude(rows, col = -1 ):
    if (col == -1): 
        col = len(rows[0]) - 1
    mag = 0
    for row in rows:
        mag += math.pow( row[col] , 2)* 1.0
    
    n = len (rows)    
    mag = math.sqrt(mag)
    return mag   

# Take the last column and 
def variance(rows, col = -1 ):
    if (col == -1): 
        col = len(rows[0]) - 1
    var = 0
    for row in rows:
        var += math.pow( row[col] , 2)* 1.0
    
    n = len (rows)    
    var /= n-1
    return var

# Take the last column and 
def average(rows, col = -1 ):
    if (col == -1): 
        col = len(rows[0]) - 1
    avg = 0
    for row in rows:
        avg += row[col] * 1.0;
    
    n = len (rows)    
    avg /= n
    return avg
 
 
    def log2(x):
        return 0
        

# Information gain between parent and children
# current score, is parent score.
#

def informationGain (parentScore, parentRows, childL, childR, scoref=entropy):

    p=float(len(childL))/len(parentRows)
    gain=parentScore-p*scoref(childL)-(1-p)*scoref(childR)
    return gain;


# Max depth of b-tree
# Min Inputs required
# Min Gini
def stoppingCriteria (rows, nodeId):

    MIN_GINI = 0.01
    MIN_INPUTS = 1
    MAX_DEPTH = 6
    
    gini = giniimpurity(rows)
    inputs = len(rows)
    
    depth = math.floor( math.log(nodeId,2) ) 
    
    
    if ( gini < MIN_GINI):
        return True
    
    if ( inputs < MIN_INPUTS):
        return True
    
    if ( depth > MAX_DEPTH):
        return True
    
    return False

# This is he predictionis the just the average of the row values
def findPrediction (rows):
    return average(rows)
    


def getChildNodeId (nodeId):
    depth = math.floor( math.log(nodeId,2) )
    firstNodeAtPrev = math.pow(2,depth)
    
    childNodeId = math.pow(2,depth+1) +  (nodeId - firstNodeAtPrev ) * 2 
    return int ( childNodeId )



def controller (theData):
    
    #1.  while we have more loops, open file and readIds.  First time, we start from scratch
    userDataFilePath = './data/modeldata.csv'
    modelFileOrig = planetModel.planetModel(userDataFilePath)
    modelFileOrig.flushFile()

    
    moreNodes = True
    depth = 0
    while (moreNodes):
        
        moreNodes = False
        modelFile = planetModel.planetModel(userDataFilePath)
        modelFile.readFile()
        

        
    #2. For each id
        applicableData = []
        ids = []
        if ( depth == 0):
            ids = [1]    
            modelFile.appendData(1, -1, -1, -1)
        else:
            ids = modelFile.getNodeIdsAtDepth(depth)
            
        for id in ids:
            if ( depth == 0):
                applicableInputs = theData
            else:
                applicableInputs = modelFile.getApplicableInputsforNodeId(id, theData)
                #TBD get all nodes for this depth
            #applicableData =
         
            #2b. Find applicable nodes
     
            #2c. find best split Mr jobs
            modelNode = bestSplit(applicableInputs, id )            
    
            if ( modelNode.id == None ):
                continue
                
            #2d. Write to file
            if (modelNode.col != -1):
                modelFile.addPredicate(modelNode.id, modelNode.col, modelNode.split, modelNode.count)                
                moreNodes = True
            else:
                modelFile.addPredicate(modelNode.id, -1, -1, modelNode.count)
            #2d. increment stuff
            modelFile.flushFile()            
        depth = depth +1
    
    return 1
    
    
def bestSplit(rows, nodeId, scoref=entropy):
 
    if len(rows)==0: return ModelNode( )
    
    #Jag, increase the number of nodes allowed for pure node

    if ( stoppingCriteria (rows, nodeId ) ):
        return ModelNode(id=nodeId, count=len(rows))
         
    current_score=scoref(rows)
    
    # Set up some variables to track the best criteria
    # We just loop through each posibility to find the best split.
    # Then we takes those sets and call recurively down to the children nodes.
    best_gain=0.0
    best_criteria=None
    best_sets=None
    column_count=len(rows[0])-1 
    for col in range(0,column_count):
    # Generate the list of different values in
    # this column
        column_values={}
        for row in rows:
            column_values[row[col]]=1
        # Now try dividing the rows up for each value
        # in this column
        # This is a bit inefficient, it could sort values and find midpoint rather than this way.
        for value in column_values.keys( ):
            (set1,set2)=divideset(rows,col,value)
        
        # Information gain
            gain=informationGain (current_score, rows, set1, set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=(col,value)
                best_sets=(set1,set2)
    # Create the subbranches
    if best_gain>0:
        return ModelNode( id=nodeId, col=best_criteria[0], split=best_criteria[1], count=len(rows))
    else:
        return ModelNode( id=nodeId, count=len(rows) )
    

# buildtree - main function for tree building
# 
#
# returns descision node, that contains the split, or pure node if no split
#
def buildtree(rows,nodeId,scoref=entropy):
    
    
    if len(rows)==0: return decisionnode( )
    
    #Jag, increase the number of nodes allowed for pure node
    if ( stoppingCriteria (rows, nodeId ) ):
        return decisionnode(id=nodeId, results=uniquecounts(rows) )
         
    current_score=scoref(rows)
    
    # Set up some variables to track the best criteria
    # We just loop through each posibility to find the best split.
    # Then we takes those sets and call recurively down to the children nodes.
    best_gain=0.0
    best_criteria=None
    best_sets=None
    column_count=len(rows[0])-1 
    for col in range(0,column_count):
    # Generate the list of different values in
    # this column
        column_values={}
        for row in rows:
            column_values[row[col]]=1
        # Now try dividing the rows up for each value
        # in this column
        # This is a bit inefficient, it could sort values and find midpoint rather than this way.
        for value in column_values.keys( ):
            (set1,set2)=divideset(rows,col,value)
        
        # Information gain
            gain=informationGain (current_score, rows, set1, set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain=gain
                best_criteria=(col,value)
                best_sets=(set1,set2)
    # Create the subbranches
    if best_gain>0:
        childNodeId = getChildNodeId(nodeId )
        trueBranch=buildtree(best_sets[0], childNodeId  ) 
        falseBranch=buildtree(best_sets[1], childNodeId + 1  ) 
        return decisionnode( id=nodeId, col=best_criteria[0],value=best_criteria[1],tb=trueBranch,fb=falseBranch ) # This is node that has choices
    else:
        return decisionnode( id=nodeId, results=uniquecounts(rows) ) # this is a leaf node, we cannot do any better

def printtree(tree,indent=''):
    
    # Is this a leaf node? Then print out the count of each of the class labels.
    if tree.results!=None:
        print 'N' + str(tree.id) + ' ' + str(tree.results)
    else:
        # Print the criteria
        print 'N' + str(tree.id)+' ' + str(tree.col)+':'+str(tree.value)+'? '
        # Print the branches
        print indent+'T->',
        printtree(tree.tb,indent+' ')
        print indent+'F->',
        printtree(tree.fb,indent+' ')
                    
#main - run as 
# python
# import(treepredict)
# reload(treepredict)
# treepredict.giniimpurity(treepredict.my_data)
# treepredict.entropy ( treepredict.my_data)
# set1,set2=treepredict.divideset ( treepredict.my_data, 2, 'yes') 
#
# Commnad line example
# python -c 'import treepredict; print treepredict.giniimpurity(treepredict.my_data)'        

def main() :    
    
    parser = OptionParser(" Usage: treepredict --dataFile data/observations.json")
    parser.add_option('-d', '--dataFile', type = 'string', dest='dataFile',
                            help='Pass in a user generated file')

    (options, args) = parser.parse_args()
    print options;
    
    if ( options.dataFile <> None ) :
        print "yes"
        filePath = options.dataFile; 
        fileIn = open(filePath)
        paramJson = fileIn.read()
        fileIn.close()
        loadRows = json.loads( paramJson )
        
        #Get rid of first two columns
        theData = []
        for row in loadRows: 
            rowCol = row[ 2 : (len(row)) ]
            theData.append(rowCol)
        
    else :
        theData = my_data


    # use map reduce version
    controller(theData)
    print "finished controller job succesfully"
    
    return 1
    # This is the default buld treee
    startNodeId = 1 #level depth=0
    tree=buildtree(theData, startNodeId)
    printtree(tree)
    print "Global Data"
    print "giniImpurity:"
    print giniimpurity(theData)
    print "entropy:"
    print entropy ( theData)
    print "magnitude:"
    print magnitude ( theData)
    print "variance:"
    print variance ( theData)
    print "average:"
    print average ( theData)
    
    #jag = planetModel.planetModel(6)
    #number = jag.doMagic(5)
    #print "jag" +  str ( number )    
    

if __name__ == '__main__':
    main()