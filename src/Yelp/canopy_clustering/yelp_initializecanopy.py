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
        
    def mapper(self, key, value):
        """
        Key - is the business: or user:
        Value - the set of ratings for the user/business
        """

        #Stupid thing does not split on tabs.
        key, value = value.split("\t")
        type,id = key.replace('"','').split(":")

        if type != "business":
            return

        rating_vector = json.loads(value)

        covered = False
        for center in self.canopy:
            t1 = CorrelationMr.jaccard_full(rating_vector, center["rating_vector"])

            if t1 < T1_Business:
                covered = True

        if not covered:
            print id, rating_vector
            self.canopy.append( { 'business':id, 'rating_vector':rating_vector } )



    def mapper_final(self):
        """
        Here we yield the canopies and the centers
        Should we reduce the centers.

        Should we merge the users?? into a single vector for the canopy?
        Because the center
        """

        for center in self.canopy:
            print center
            yield center['business'], json.dumps(center["rating_vector"])
        
    def reducer(self, key, value):
        """
        Write unique set of canopy centers
        """

        for rating_vector in value:
            rating_vector_data = json.loads(rating_vector)
            #print "reducer:%s,%s" % (key, value)

        yield key, rating_vector_data


if __name__ == '__main__':
    InitializeCanopy.run()