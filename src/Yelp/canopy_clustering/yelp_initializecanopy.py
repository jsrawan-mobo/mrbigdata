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
        self.count = 0


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
        for center in self.canopy:
            t1 = CorrelationMr.jaccard_full(rating_vector, center[1]["rating_vector"])

            if t1 > T1_Business:
                #print "isCovered"
                covered = True
                center[1]["count"] += 1


        if not covered:
            #print id, rating_vector
            self.canopy.append(  [ id,  {'rating_vector':rating_vector, "count" : 1 } ] )
        if False: yield 1,2


    def mapper_final(self):
        """
        Here we yield the canopies and the centers
        Should we reduce the centers?  For now lets leave this until
        we run on hdfs.

        Should we merge the users?? into a single vector for the canopy?
        Because the center
        """

        for center in self.canopy:
            yield 1, center
        
    def reducer(self, key, value):
        """
        Write unique set of canopy centers
        """

        canopy_cent = {}
        for center_data in value:
            #print "reducer:%s,%s" % (key, value)
            canopy_cent[ center_data[0] ] = center_data[1]
            print center_data[0]

        fullPath = os.path.join(self.options.pathName, 'canopy_centers_1.txt')
        fileOut = open(fullPath,'w')
        #TODO, we should pretty format this, even though its a big dictionary.
        fileOut.write(json.dumps(canopy_cent))
        fileOut.close()



if __name__ == '__main__':
    InitializeCanopy.run()