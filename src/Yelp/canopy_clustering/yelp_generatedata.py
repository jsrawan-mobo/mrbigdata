'''

Created on Feb 09, 2013

This file will load

'''
import os
from mrjob.job import MRJob

from numpy import mat, zeros, shape, random, array, zeros_like
from random import sample
import json


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

class YelpGenerateData(MRJob):
    DEFAULT_PROTOCOL = 'json'

    def __init__(self, *args, **kwargs):
        super(YelpGenerateData, self).__init__(*args, **kwargs)

    def configure_options(self):
        super(YelpGenerateData, self).configure_options()

    def mapper(self, key, value):


        row = json.loads(value)
        if row["type"] == "review":
            business_key ="business:%s" % row['business_id']
            yield (business_key, json.dumps( [ row["user_id"], row["stars"] ] ) )

            user_key ="user:%s" % row['user_id']
            yield (user_key,  json.dumps( [ row["business_id"], row["stars"] ] ) )


    def reducer(self, key, xjIn):
        """
        Now just yield the key and all of its values in one big go
        """
        items = []
        for xj in xjIn:
            x = json.loads(xj)
            items.append(x)

        yield key, items

if __name__ == '__main__':
    YelpGenerateData.run()