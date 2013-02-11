"""
2) Come up with a set of Canopy Clusters, where each point in the space is a Business
and the distance is set to the similarity betwen ratings.
For each new business, if its within T1 of a given cluster center, then we pass through, otherwise we ignore
The Reducer is responsible for merging Canopy Clusters, that have center within a tolerance (and building a circle that encompases both)
Inputs: Business_id, list(user_id, rating)
Output: Cx,Cy => list(user,ratings)

"""
import os
from mrjob.job import MRJob
from mrjob.protocol import RawValueProtocol

from numpy import mat, zeros, shape, random, array, zeros_like
from random import sample
import json
from constants import T1_Business
from corr import CorrelationMr


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

class InitializeCanopy(MRJob):
    DEFAULT_PROTOCOL = RawValueProtocol
    
    def __init__(self, *args, **kwargs):
        super(InitializeCanopy, self).__init__(*args, **kwargs)
        self.canopy = []                  #current centroid list
        self.business_to_canopies = dict()


    def configure_options(self):
        super(InitializeCanopy, self).configure_options()
        self.add_passthrough_option(
                   '--pathName', dest='pathName', default="data", type='str',
                   help='pathName: relative pathname to current folder canopy_center_1.txt is stored')
        
    def mapper(self, key, value):
        """
        Key - is the business: or user:
        Value - the set of ratings for the user/business

        Note we have a dimensional reduction from 12K to 3K, so each cluster
        has an average of 4 related business, and they are all over the globe.
        """

        #Stupid thing does not split on tabs.
        key, value = value.split("\t")
        type,id = key.replace('"','').split(":")
        if type != "business":
            return

        rating_vector = json.loads(value)

        covered = False
        for i,center in enumerate(self.canopy):
            t1 = CorrelationMr.jaccard_full(rating_vector, center["centroid"])

            if t1 > T1_Business:
                #print "isCovered"
                #@TODO, this is cheating, what happens, we don't have cluster yet, the user won't be assigned!
                covered = True
                center["count"] += 1

                if id not in self.business_to_canopies:
                    self.business_to_canopies[id] = list()
                self.business_to_canopies[id].append(i)
#                for user, rating in rating_vector.iteritems():
#                    if user in center[1]["user_vector"]:
#                        center[1]["user_vector"][user] += rating
#                    else:
#                        center[1]["user_vector"][user] = rating

        if not covered:
            #print id, rating_vector
            self.canopy.append(   {'centroid':rating_vector, "count" : 1} )
            i = len(self.canopy)-1
            self.business_to_canopies[id] = [i]
        if False: yield 1,2


    def mapper_final(self):
        """
        Here we yield the canopies and the centers
        Should we reduce the centers?  For now lets leave this until
        we run on hdfs.

        Should we merge the users?? into a single vector for the canopy?
        Because the center
        """

        for id, canopy_vector in self.business_to_canopies.iteritems():
            yield 1, [id,canopy_vector]
        
    def reducer(self, key, value):
        """
        Write unique set of canopy centers
        """

        canopy_cent = {}
        for center_data in value:
            canopy_cent[ center_data[0] ] = center_data[1]

        fullPath = os.path.join(self.options.pathName, 'canopy_centers_1.txt')
        fileOut = open(fullPath,'w')
        #TODO, we should pretty format this, even though its a big dictionary.
        fileOut.write(json.dumps(canopy_cent))
        fileOut.close()



if __name__ == '__main__':
    InitializeCanopy.run()