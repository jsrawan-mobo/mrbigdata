'''
Created on May 20, 2011

@author: jsrawan
'''
import math

class rowMath(object):
    '''
    classdocs
    '''
    rows = []    

    def __init__(self, rowsIn):
        '''
        Constructor
        '''
        self.rows = rowsIn
        
    def divideset(self, column,value):
            # Make a function that tells us if a row is in
            # the first group (true) or the second group (false)
            split_function=None
            if isinstance(value,int) or isinstance(value,float):
                split_function=lambda row:row[column]>=value  #note larger than equal to for left node.
            else:
                split_function=lambda row:row[column]==value
            # Divide the rows into two sets and return them
            set1=[row for row in self.rows if split_function(row)]
            set2=[row for row in self.rows if not split_function(row)]
            return (set1,set2)
        
    # Information gain between parent and children
    # current score, is parent score.
    #
    
    def informationGain (self,parentScore, childL, childR):
    
        p=float(len(childL))/len(self.rows)
        
        rL = rowMath(childL)
        rR = rowMath(childR)
        
        gain=parentScore-p*rL.entropy()-(1-p)*rR.entropy()
        return gain;

        
        
    # Create counts of possible results (the last column of
    # each row is the result)
    # Takes the class label, and does a count(label)
    # Return is a list of counts for each output label.
    # i.e. label1=10, label2=10
    def uniquecounts(self):
        results={}
        for row in self.rows:
        # The result is the last column
            r=row[len(row)-1]
            if r not in results: results[r]=0
            results[r]+=1
        return results
        
        
    # Probability that a randomly placed item will
    # be in the wrong category
    # This code is super wierd, instead of 1- sum-square impurities
    # It does dot product instead, but the numbers come out the same.
    def giniimpurity(self):
        total=len(self.rows)
        counts=self.uniquecounts()
        imp=0
        for k1 in counts:
            p= math.pow((float(counts[k1])/total),2)
            imp+=p
        imp = 1- imp
        return imp
    
    # Entropy is the sum of p(x)log(p(x)) across all
    # the different possible results
    def entropy(self):
        from math import log
        log2=lambda x:log(x)/log(2)
        results=self.uniquecounts()
        # Now calculate the entropy
        ent=0.0
        for r in results.keys( ):
            p=float(results[r])/len(self.rows)
            ent=ent-p*log2(p)
        return ent        
    # Perform variance on class lables for the given node
    # BestSplit = D * Var(D) -Dl*Var(Dl) + Dr+Var(Dr))
    # This is when output is numerical
    def splitVariance(self, childL, childR):
        
        
        magD = self.magnitude (self.rows )
        magDl = self.magnitude (childL)
        magDr = self.magnitude (childR )
        varD  = self.variance(self.rows)
        varDl = self.variance(childL)
        varDr = self.variance(childR)
        
        
        splitVar = magD * varD - ( magDl * varDl + magDr * varDr )
        
        return splitVar
        
    
    
    # Take the last column and 
    def magnitude(self, col = -1 ):
        if (col == -1): 
            col = len(self.rows[0]) - 1
        mag = 0
        for row in self.rows:
            mag += math.pow( row[col] , 2)* 1.0
        
        n = len (self.rows)    
        mag = math.sqrt(mag)
        return mag   
    
    # Take the last column and 
    def variance(self, col = -1 ):
        if (col == -1): 
            col = len(self.rows[0]) - 1
        var = 0
        avg = self.average()
        for row in self.rows:
            var += math.pow( row[col] - avg, 2)* 1.0
            
        
        n = float ( len (self.rows) )    
        if (n>1):
            var /= n-1
        else:
            var = 0
        return var
    
    # Take the last column and 
    def average(self, col = -1 ):
        if (col == -1): 
            col = len(self.rows[0]) - 1
        avg = 0
        for row in self.rows:
            avg += row[col] * 1.0;
        
        n = len (self.rows)    
        avg /= n
        return avg        