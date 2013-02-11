"""
Various Correlatoins and Math measurements here used in Mapreduce CR
Gleamed from various sources.
"""


import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))



class CorrelationMr(object):


    @classmethod
    def cosine(cls,dot_product, rating_norm_squared, rating2_norm_squared):
        '''
        The cosine between two vectors A, B
        dotProduct(A, B) / (norm(A) * norm(B))
        '''
        numerator = dot_product
        denominator = rating_norm_squared * rating2_norm_squared

        return (numerator / (float(denominator))) if denominator else 0.0

    @classmethod
    def jaccard_full(cls, object1, object2):
        """
        Does jaccard on just counts, not dot product
        """

        keys_in_common = filter(object1.has_key, object2.keys())
        keys_in_common_count = len(keys_in_common)
        #print keys_in_common
        #if keys_in_common_count > 0:
            #print "keys= %s, value=%s" % ( keys_in_common, len(object1) + len(object2))
        union_count = len(object1) + len(object2) - keys_in_common_count

        return (keys_in_common_count / (float(union_count))) if union_count else 0.0

    @classmethod
    def jaccard_dot(cls, object1, object2):
        """
        Does jacard on dot products
        """

        keys_in_common = filter(object1.has_key, object2.keys())
        keys_in_common_sum =  sum (object1[key] * object2[key] for key in keys_in_common)
        #print keys_in_common
        #if keys_in_common_count > 0:
            #print "keys= %s, value=%s" % ( keys_in_common, len(object1) + len(object2))

        union_sum = sum(object1.values()) + sum(object2.values()) - keys_in_common_sum

        return (keys_in_common_sum / (float(union_sum))) if union_sum else 0.0

    @classmethod
    def pearson_correlation(cls, object1, object2):
        values = range(len(object1))

        # Summation over all attributes for both objects
        sum_object1 = sum([float(object1[i]) for i in values])
        sum_object2 = sum([float(object2[i]) for i in values])

        # Sum the squares
        square_sum1 = sum([pow(object1[i],2) for i in values])
        square_sum2 = sum([pow(object2[i],2) for i in values])

        # Add up the products
        product = sum([object1[i]*object2[i] for i in values])

        #Calculate Pearson Correlation score
        numerator = product - (sum_object1*sum_object2/len(object1))
        denominator = ((square_sum1 - pow(sum_object1,2)/len(object1)) * (square_sum2 -
            pow(sum_object2,2)/len(object1))) ** 0.5

        # Can"t have division by 0
        if denominator == 0:
            return 0

        result = numerator/denominator
        return result