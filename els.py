from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
es = Elasticsearch()

def lines():
    for row in rows:
        d = {k: row[k] for k in row.keys()}
        d['_op_type'] = 'index'
        d['_index']= 'chat'
        d['_type']= 'message'
        yield d


bulk(es,lines())
