__author__ = 'Roland'
import argparse

parser = argparse.ArgumentParser(description='Process Digsby, Trillian and Pidgin Logs and output YAML files.',
                                epilog=
"The output will contain the datetime of the message, the id of the sender and the message itself as a list, \
each a YAML document")
parser.add_argument('integers', metavar='N', type=int, nargs='+',
    help='an integer for the accumulator')
parser.add_argument('--sum', dest='accumulate', action='store_const',
    const=sum, default=max,
    help='sum the integers (default: find the max)')

args = parser.parse_args()
print(args.accumulate(args.integers))
if not (len(sys.argv) > 2 and sys.argv[1] == "clear"):
    for root, dirs, files in os.walk('logs'):
        for file in files:
            os.remove(os.path.join(root,file))
