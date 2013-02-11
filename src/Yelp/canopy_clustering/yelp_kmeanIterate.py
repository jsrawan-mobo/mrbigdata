'''
Created on Apr 18, 2011

@author: mike-bowles
'''
import os
from mrjob.job import MRJob

from math import sqrt
from numpy import mat, zeros, shape, random, array, zeros_like
from random import sample
import json
from constants import T2_Business
from corr import CorrelationMr

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

def dist(x,y):
    #euclidean distance between two lists    
    sum = 0.0
    for i in range(len(x)):
        temp = x[i] - y[i]
        sum += temp * temp
    return sqrt(sum)

def plus(x,y):
    #"vector" sum of two lists
    length = len(x)
    sum = [0.0]*length
    for i in range(length):
        sum[i] = x[i] + y[i]
    return sum
        
def divide(x,alpha):
    length = len(x)
    div = [0.0]*length
    for i in range(length):
        div[i] = x[i]/alpha
    return div

class MRkMeansIter(MRJob):
    DEFAULT_PROTOCOL = 'json'
    
    def __init__(self, *args, **kwargs):
        """
        This assumes a centroid file is the INPUT.
        BASICALLY each iteration re-assigns if centers move.
        If centers don't move, you have zero error reduction and
        the iteration would be superflous.

        The SELF does not maintain state between mapper and reducer.
        and for mapper_final and reducer_final.
        """
        super(MRkMeansIter, self).__init__(*args, **kwargs)
        self.new_centroid = {}
        fullPath = os.path.join(self.options.pathName , 'canopy_centers_1.txt')

        fileIn = open(fullPath)
        centroidsJson = fileIn.read()
        fileIn.close()
        self.canopy = json.loads(centroidsJson)


        #Now cheat and just assign canopy = centroids for now!!
        # Each centroid, is just a single user that represent the center.
        # As it mutates, we'll adjust the center's ratings.
        # The average, will also represent, the recommendation for adjacent business

        for business_id, canopy_vector in self.canopy.iteritems():
            #print k
            for k_i in canopy_vector:
                self.new_centroid[k_i] = {}
        #print  len(self.new_centroid.keys())


        #self.numMappers = 1             #number of mappers
        #self.count = 0                  #passes through mapper
        #self.count2 = []                #contributors to new_centroid calc in each mapper
                                                 
    def configure_options(self):
        super(MRkMeansIter, self).configure_options()
        self.add_passthrough_option(
                   '--pathName', dest='pathName', default="data", type='str',
                   help='pathName: relative pathname to current folder canopy_center_1.txt is stored')
        
    def mapper(self, key, value):
        """
        So the value are the user vectors.  Here we want to index the
        Business the users has rated as the canopies, but use the jaccard
        to compare with all kmean centers which ARE USERS in a different hyperplane.
        """

         #Stupid thing does not split on tabs.
        key, value = value.split("\t")
        type,id = key.replace('"','').split(":")
        if type != "user":
            return

        user_rating_vector = json.loads(value)

        #The user rating vector, has business as key and rating as key
        #Here we do the real assignment.
        canopy_keys_intersect = list()

        canopy_keys_intersect = filter(user_rating_vector.haskey,self.canopy().keys())

#        for canopy_key, canopy_data in self.canopy():
#            if id in canopy_data["user_vector"].keys():
#                canopy_keys_intersect.append(canopy_key)

        if not len(canopy_keys_intersect):
            print "Cannot find cluster for user, skipping"
            return

        km_key = (0,0)
        for canopy_key in canopy_keys_intersect:
            #print  len(self.new_centroid.keys())
            print canopy_key
            for user_key, rating_vector in self.new_centroid[canopy_key].iteritems():
                t2 = CorrelationMr.jaccard_dot(user_rating_vector, rating_vector["centroid_vector"])
                print t2
                if t2 > T2_Business and self.new_centroid[km_key[0]][km_key[1]]:
                    km_key = (canopy_key, user_key)
                    print "covered"

        if km_key == (0,0):
            print "new"
            #So its in many centroid keys, and is not a center, lets make it one in the first centroid
            canopy_key = canopy_keys_intersect[0]
            user_key = id
            centroid_obj = { "centroid" : user_rating_vector, "users_vector" : [user_rating_vector], "count" : 1}
            self.new_centroid[key] = dict()
            self.new_centroid[key][user_key] = centroid_obj
        else:
            key = km__key[0]
            user_key = km__key[1]
            self.new_centroid[key][user_key]["users_vector"].append(user_rating_vector)
            self.new_centroid[key][user_key]["count"] += 1
        if False: yield 1,2

    def mapper_final(self):
        """
        Just output the centroids, nothing else.
        """
        print "done"
        for cluster_key, km_clust in self.new_centroid.iteritems():
            for user_key, user_obj in km_clust.iteritems():
                yield 1, {user_key:user_obj}

    def reducer(self, key, value):

        """
        Each xs is a set of centroids and counts, we get one for each mapper that was run
        We have to add each index from each mapper
        add up the centroid sums from all the mappers
        add up the number of points in each centroid calc from each mapper
        """
        kmean_cent = {}
        for center_data in value:
            #print "reducer:%s,%s" % (key, value)
            kmean_cent[ center_data[0] ] = center_data[1]
            #print center_data[0]

        #write new centroids to file
        fullPath = os.path.join(self.options.pathName, 'kmean_centers_1.txt')
        fileOut = open(fullPath,'w')
        #TODO, we should pretty format this, even though its a big dictionary.
        fileOut.write(json.dumps(kmean_cent))
        fileOut.close()

        #Again no yield.

    #def steps(self):
        #return ([self.mr(mapper=self.mapper,reducer=None,mapper_final=None)])
            


def main():
    MRkMeansIter.run()
if __name__ == '__main__':
    main()
