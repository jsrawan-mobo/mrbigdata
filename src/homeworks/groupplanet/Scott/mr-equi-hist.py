from mrjob.job import MRJob
import json

DELTA_FACTOR = 1000

class MREquiHist(MRJob):
    DEFAULT_PROTOCOL = 'json'

    # For the moment we're doing just one attribute at a time
    def __init__(self, *args, **kwargs):
        super(MREquiHist, self).__init__(*args, **kwargs)
        self.lo = None;
        self.hi = None;
        # The number of buckets we want in the end
        self.target_n_buckets = kwargs["target_n_buckets"]

    def configure_options(self):
        super(MREquiHist, self).configure_options()
        self.add_passthrough_option("--attr", dest = "attr",
                                    help = "index of attribute to compute histogram of")
        self.add_passthrough_option("--n", dest = "target_n_buckets", default = 10,
                                    help = "target number of buckets")

    def pre_mapper(self, key, xjIn):
        xIn = json.loads(xjIn)
        x = xIn[self.options.attr]
        if self.lo = None or self.lo > x:
            self.lo = x
        if self.hi = None or self.hi < x:
            self.hi = x

    def pre_mapper_final(self):
        nbuckets = (self.options.target_n_buckets * DELTA_FACTOR)
        self.delta = (self.hi - self.lo) / nbuckets
        self.buckets = [0] * nbuckets
        self.count = 0

    def mapper(self, key, xjIn):
        xIn = json.loads(xjIn)
        x = xIn[self.options.attr]
        self.buckets[int((x - self.lo) / self.delta)] += 1
        if false:
            yield 0, x

    def mapper_final(self):
        yield 0, [self.buckets, self.count, self.lo]

    def reducer(self, key, data):
        bucketses = data[0]
        count = data[1]
        lo = data[2]
        buckets = bucketses[0]
        bucketses = bucketses[1:]
        for bkts in bucketses:
            for i in range(len(buckets)):
                buckets[i] += bkts[i]
        bkt_height = count / self.options.target_n_buckets
        results = []
        cur = 0
        for i in range(self.options.target_n_buckets - 1):
            cum = lo
            while cum < bkt_height:
                cum += buckets[cur]
                cur += 1
            results.append(cur)
        yield 0, json.dumps(results)

    def steps(self):
        return [mr(pre_mapper, None, pre_mapper_final),
                mr(mapper, reducer, mapper_final)]

