"""
Here we should go to the original business list and print out avg, max, mean, std, count, for each of the following things


If we are doing it right

Business
->business list:count =>  We should have a small set of business
->star_rating:avg,max,mean,std,count =>
->categories: restaurant, japenese =>
->lat/long:avg, min, max, std => Should be a very small std
"""






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

class YelpDumpStats(MRJob):
    DEFAULT_PROTOCOL = 'json'

    def __init__(self, *args, **kwargs):
        super(YelpDumpStats, self).__init__(*args, **kwargs)


        fullPath = os.path.join(self.options.pathName, 'yelp_business_all.json')
        fileIn = open(fullPath)

        self.business_rec = dict()
        for line in fileIn.readlines():
            business = json.loads(line)
            self.business_rec[business["business_id"]] = business
        fileIn.close()
        #print len(self.business_rec)



    def configure_options(self):
        super(YelpDumpStats, self).configure_options()
        self.add_passthrough_option(
                   '--pathName', dest='pathName', default="data", type='str',
                   help='pathName: relative pathname to current folder yelp_business_all.json is stored')


    def mapper(self, key, value):

        #Stupid thing does not split on tabs.
        key, value = value.split("\t")
        kmeans_id,canopy_id = key.replace('"','').split(":")
        user_rating_vector = json.loads(value)

        business_stats = dict()
        global_stats = dict()
        global_stats["latitude.sum"] = 0
        global_stats["latitude.count"] = 0
        global_stats["latitude.max"] = -90
        global_stats["latitude.min"] = 90

        global_stats["longitude.sum"] = 0
        global_stats["longitude.count"] = 0
        global_stats["longitude.max"] = -90
        global_stats["longitude.min"] = 90

        for user_id, business_vector in  user_rating_vector.iteritems():

            for business_id, business_rating in business_vector.iteritems():

                business = self.business_rec[business_id]

                if business_id not in business_stats:
                    business_stats[business_id] = dict()
                    business_stats[business_id]["name"] = business["name"]
                    business_stats[business_id]["count"] = 0
                    business_stats[business_id]["star"] = dict()
                    business_stats[business_id]["star.sum"] = 0
                    business_stats[business_id]["star.count"] = 0
                    business_stats[business_id]["star.max"] = 0
                    business_stats[business_id]["star.min"] = 99


                business_stats[business_id]["count"] += 1
                business_stats[business_id]["star.sum"] += float(business_rating)
                business_stats[business_id]["star.count"] += 1
                business_stats[business_id]["star.max"] = max(business_rating, business_stats[business_id]["star.max"])
                business_stats[business_id]["star.min"] = min(business_rating, business_stats[business_id]["star.min"])

                for cat in business["categories"]:
                    cat_key = "cat:%s" % cat
                    if cat_key not in global_stats:
                        global_stats[cat_key] = 0
                    global_stats[cat_key] += 1

                global_stats["latitude.sum"] += business["latitude"]
                global_stats["latitude.count"] += 1
                global_stats["latitude.max"] = max(business["latitude"],global_stats["latitude.max"])
                global_stats["latitude.min"] = min(business["latitude"],global_stats["latitude.min"])

                global_stats["longitude.sum"] += business["longitude"]
                global_stats["longitude.count"] += 1
                global_stats["longitude.max"] = max(business["longitude"],global_stats["longitude.max"])
                global_stats["longitude.min"] = min(business["longitude"],global_stats["longitude.min"])

        for business_id, business_stat in business_stats.iteritems():
            business_stat["star.avg"] = business_stat["star.sum"] / business_stat["star.count"]

        global_stats["longitude.avg"] = global_stats["longitude.sum"] / global_stats["longitude.count"]
        global_stats["latitude.avg"] = global_stats["latitude.sum"] / global_stats["latitude.count"]


        #print kmeans_id, global_stats, business_stats
        yield str(kmeans_id), [global_stats, business_stats]
        #yield kmeans_id, 1

    def reducer(self, key, value):
        """
        Here we could do some global stats if we want.
        Ideally, we can sort by the idealness of fit and print overall stats.
        """
        yield key, value

if __name__ == '__main__':
    YelpDumpStats.run()