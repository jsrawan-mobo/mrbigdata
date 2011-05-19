


from optparse import OptionParser
import json
import math


my_data=[['slashdot','USA','yes',18,'None'],
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
class decisionnode:
    def __init__(self,col=-1,value=None,results=None,tb=None,fb=None):
        self.col=col
        self.value=value
        self.results=results
        self.tb=tb
        self.fb=fb
        
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

# Information gain between parent and children
# current score, is parent score.
#

def informationGain (parentScore, parentRows, childRows1, childRows2, scoref=entropy):

    p=float(len(childRows1))/len(parentRows)
    gain=parentScore-p*scoref(childRows1)-(1-p)*scoref(childRows2)
    return gain;

# buildtree - main function for tree building
# 
#
#
#
def buildtree(rows,scoref=entropy):
    
    
    if len(rows)==0: return decisionnode( )
    
    #Jag, increase the number of nodes allowed for pure node
    if len(rows) < 10: return decisionnode(results=uniquecounts(rows) )
    
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
        trueBranch=buildtree(best_sets[0])
        falseBranch=buildtree(best_sets[1])
        return decisionnode( col=best_criteria[0],value=best_criteria[1],tb=trueBranch,fb=falseBranch )
    else:
        return decisionnode( results=uniquecounts(rows) )

def printtree(tree,indent=''):
    
    # Is this a leaf node? Then print out the count of each of the class labels.
    if tree.results!=None:
        print str(tree.results)
    else:
        # Print the criteria
        print str(tree.col)+':'+str(tree.value)+'? '
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

    tree=buildtree(theData)
    printtree(tree)
    print "giniImpurity:"
    print giniimpurity(theData)
    print "entropy:"
    print entropy ( theData)
    

if __name__ == '__main__':
    main()