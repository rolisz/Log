if __package__ is None:
    import sys
    from os import path
    sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import conversation
import parsers
import json

import collections
import itertools
messages = collections.defaultdict(list)
for contact, text in parsers.Whatsapp("../Whatsapp"):
    messages[contact].append(text)
for contact in messages:
    messages[contact] = list(itertools.chain.from_iterable(messages[contact]))
    messages[contact].sort(key=lambda x: x['timestamp'])

output_file = open("replies.json", "w")

data = {}

for k in messages:
    data[k] = {}
    data[k]['x'] = [x['timestamp'].isoformat() for x in messages[k]]
    data[k]['y'] = [len(x['message']) for x in messages[k]]

json.dump(data, output_file)
