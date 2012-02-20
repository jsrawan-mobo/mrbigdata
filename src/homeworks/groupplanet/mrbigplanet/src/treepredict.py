
# import sys
# sys.path.append('/usr/lib/pyshared/python2.6')
# sys.path.append('/usr/lib/graphviz/python/')    # 32-bits
# sys.path.append('/usr/lib64/graphviz/python/')  # 63-bits
# sys.path.append('/usr/lib/pyshared/python2.6/pygraphviz')   #graph
# import gv 

import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
import gv

from optparse import OptionParser
import json
import math

# Import pygraph
from pygraph.classes.graph import graph
from pygraph.classes.digraph import digraph
from pygraph.algorithms.searching import breadth_first_search
from pygraph.readwrite.dot import write

import Image
#from gv import write
#from gv import readstring
#from pygraph import graph
#from pygraph import digraph
#from pygraph.readwrite.dot import write


from commonLib import planetModel
from commonLib import rowMath


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



# Max depth of b-tree
# Min Inputs required
# Min Gini
def stoppingCriteria (rows, nodeId):

    MIN_GINI = 0.01
    MIN_INPUTS = 1
    MAX_DEPTH = 6
    
    r = rowMath.rowMath(rows)
    gini = r.giniimpurity()
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
    r = rowMath.rowMath(rows)
    return r.average(rows)
    


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

    modelFileFinal = planetModel.planetModel(userDataFilePath)
    modelFileFinal.readFile()
    fileName = modelFileFinal.drawGraph(theData)
    Image.open(fileName).show()

    
    return 1

def entropy(rows):
        r = rowMath.rowMath(rows)
        return r.entropy()
        
def uniquecounts(rows):
        r = rowMath.rowMath(rows)
        return r.uniquecounts()   
    
    
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
            r = rowMath.rowMath(rows)
            (set1,set2)=r.divideset(col,value)
        
        # Information gain
            gain=r.informationGain (current_score, set1, set2)
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
            r = rowMath.rowMath(rows)
            (set1,set2)=r.divideset(col,value)
        
        # Information gain
            gain= r.informationGain (current_score, set1, set2)
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
        r = rowMath.rowMath(rows)
        return decisionnode( id=nodeId, results=r.uniquecounts() ) # this is a leaf node, we cannot do any better

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
                    
def testGraph():
    gr = graph()
    gr.add_nodes(["Portugal","Spain","France","Germany","Belgium","Netherlands","Italy"])
    gr.add_nodes(["Switzerland","Austria","Denmark","Poland","Czech Republic","Slovakia","Hungary"])
    gr.add_nodes(["England","Ireland","Scotland","Wales"])
    
    gr.add_edge("Portugal", "Spain")
    gr.add_edge("Spain","France")
    gr.add_edge("France","Belgium")
    gr.add_edge("France","Germany")
    gr.add_edge("France","Italy")
    gr.add_edge("Belgium","Netherlands")
    gr.add_edge("Germany","Belgium")
    gr.add_edge("Germany","Netherlands")
    gr.add_edge("England","Wales")
    gr.add_edge("England","Scotland")
    gr.add_edge("Scotland","Wales")
    gr.add_edge("Switzerland","Austria")
    gr.add_edge("Switzerland","Germany")
    gr.add_edge("Switzerland","France")
    gr.add_edge("Switzerland","Italy")
    gr.add_edge("Austria","Germany")
    gr.add_edge("Austria","Italy")
    gr.add_edge("Austria","Czech Republic")
    gr.add_edge("Austria","Slovakia")
    gr.add_edge("Austria","Hungary")
    gr.add_edge("Denmark","Germany")
    gr.add_edge("Poland","Czech Republic")
    gr.add_edge("Poland","Slovakia")
    gr.add_edge("Poland","Germany")
    gr.add_edge("Czech Republic","Slovakia")
    gr.add_edge("Czech Republic","Germany")
    gr.add_edge("Slovakia","Hungary")
    
    # Draw as PNG
    with open("./country.viz", 'wb') as f:
        dot = write(gr,f)
        f.write(dot)
        gvv = gv.readstring(dot)
        gv.layout(gvv,'dot')
        gv.render(gvv,'png','europe.png') 
        Image.open('europe.png').show()
    
                        
#main - run as 
# python
# import treepredict
# reload treepredict 
# treepredict.entropy ( treepredict.my_data)
# set1,set2=treepredict.divideset ( treepredict.my_data, 2, 'yes') 
#
# Commnad line example
# python -c 'import treepredict; print treepredict.entropy ( treepredict.my_data)'        
#  python treepredict.py --dataFile data/observation.json

# dotty bddTree.viz
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
    #testGraph()
    return 1
    # This is the default buld treee
    startNodeId = 1 #level depth=0
    tree=buildtree(theData, startNodeId)
    printtree(tree)
    r = rowMath.rowMath(theData)
    print "Global Data"
    print "giniImpurity:"
    print r.giniimpurity()
    print "entropy:"
    print r.entropy ()
    print "magnitude:"
    print r.magnitude ()
    print "variance:"
    print r.variance ()
    print "average:"
    print r.average ()
    
    #jag = planetModel.planetModel(6)
    #number = jag.doMagic(5)
    #print "jag" +  str ( number )    
    
             

if __name__ == '__main__':
    main()
