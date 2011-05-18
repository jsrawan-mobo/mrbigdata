from mrjob.job import MRJob

import json

class MR_ExpandNodes(MRJob):
    DEFAULT_PROTOCOL = 'json'

    def __init__(self, *args, **kwargs):
        super(MR_ExpandNodes, self).__init__(*args, **kwargs)
        fileIn = "/tmp/model_info"
        model_info_json = fileIn.read()
        model_info = json.loads(model_info_json)
        self.model = model_info[0]
        self.nodes = model_info[1]
        # A list of attribute descriptors, each of the form
        # [ true, split_points ] if ordinal or interval
        # [ false, values ] if nominal
        self.attrs = model_info[3]
        # node# -> attr# -> split -> agg_tup
        self.agg_tup_map = dict()

    def configure_options(self):
        super(MR_ExpandNodes, self).configure_options()

    # The model is of the form
    #
    #  node ::= node_ID | [ node_ID, attr#, split, left, right ]
    #
    # If the split is numeric, the attribute is ordinal or interval; otherwise, it's
    # a list of attribute values as strings or integers.
    # Node IDs are integers.  If a node is represented as just an integer, it has not
    # been expanded.
    def eval_model(row):
        eval_model_at(row, self.model)

    def eval_model_at(row, node):
        if isinstance(node, int):
            return node
        attr_val = row[node[1]]
        split_val = node[2]
        if isinstance(split_val, (int, float)):
            if attr_val < split_val:
                return eval_model_at(row, node[3])
            else:
                return eval_model_at(row, node[4])
        else:
            if attr_val in split_val:
                return eval_model_at(row, node[3])
            else:
                return eval_model_at(row, node[4])

    def mapper(self, _, row_json):
        row = json.loads(row_json)
        y = row[len(row) - 1]
        node = eval_model(row)
        if node in self.nodes:
            if node not in self.agg_tup_map:
                self.agg_tup_map[node] = dict()
            attr_map = self.agg_tup_map[node]
            for iattr in range(len(row) - 1):
                if iattr not in attr_map:
                    attr_map[iattr] = dict()
                split_map = attr_map[split]
                xi = row[iattr]
                attr = self.attrs[iattr]
                if (attr[0]):	# ordinal or interval?
                    for split in attr[1]:
                        if split not in split_map:
                            split_map[split] = [0.0, 0.0, 0]
                        agg_tup = split_map[split]
                        if xi < split:
                            agg_tup[0] += y
                            agg_tup[1] += y * y
                            agg_tup[2] += 1
                else:
                    
