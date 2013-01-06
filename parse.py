__author__ = 'Roland'
import argparse
import os
import digsby
import trillian
import pidgin

types = ['digsby','trillian','pidgin']
parser = argparse.ArgumentParser(description='Process Digsby, Trillian and Pidgin Logs and output YAML files.',
                                epilog=
"The output will contain the datetime of the message, the id of the sender and the message itself as a list, \
each a YAML document")
parser.add_argument('-k','--keep', action = "store_true", default = False,
                    help = "Keep previously parse logs. Default is to delete them.")
parser.add_argument('--digsby','-d', action = "store", default = "Digsby Logs", help = "Location of Digsby logs")
parser.add_argument('--trillian','-t', default = "Trillian", help = "Location of Trillian logs")
parser.add_argument('--pidgin','-p', default = "Pidgin", help = "Location of Pidgin logs")
parser.add_argument('--dest', default = "logs", help = "Location where to put parsed logs")
parser.add_argument('--process', choices = types, nargs = '*', default = ["pidgin"])
parser.add_argument('--version', action = "version",  version='%(prog)s 0.2')

args = parser.parse_args()
print(args)
print(args.keep)
if not args.keep:
    for root, dirs, files in os.walk('logs'):
        for file in files:
            os.remove(os.path.join(root,file))

if 'digsby' in args.process:
    digsby.parse(args.digsby)

if 'trillian' in args.process:
    trillian.parse(args.trillian)

if 'pidgin' in args.process:
    pidgin.parse(args.pidgin)

