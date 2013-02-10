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

from numpy import mat, zeros, shape, random, array, zeros_like
from random import sample
import json
from constants import T1_Business
from corr import CorrelationMr


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

class InitializeCanopy(MRJob):
    DEFAULT_PROTOCOL = 'json'
    
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

        print key, value
        if not key[1:19] == "business:":
            return

        row = json.loads(value)

        covered = False
        for center in self.canopy:
            if CorrelationMr.jaccard_full(value, center["value"]) < T1_Business:
                covered = True

        if not covered == 0:
            self.canopy.append( { 'business':key, 'value':row } )



    def mapper_final(self):
        """
        Here we yield the canopies and the centers
        Should we reduce the centers.
        """

        for center in self.canopy:
            yield center['business'], json.dumps(center["value"])
        
    def reducer(self, center, value):
        """
        Write unique set of canopy centers
        """
        center_data = json.loads(value)

        yield center, center_data


if __name__ == '__main__':
    InitializeCanopy.run()