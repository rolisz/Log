__author__ = 'Roland'
import os
import re
from os.path import join, getsize
import yaml
import sys

def parse(folder = "Digsby Logs"):
    fileList = []

    for root, dirs, files in os.walk(folder):
        for file in files:
            f = os.path.join(root,file)
            fileList.append(f)
        if '.git' in dirs:
            dirs.remove('.git')  # don't visit CVS directories
        if '.idea' in dirs:
            dirs.remove('.idea')
    count = 0

    for file in fileList:
        try:
            f = open(file,encoding="utf-8")
            name = re.match("Digsby Logs\\\\rolisz\\\\(.+?)\\\\rolisz(.+?)?\\\\(.+?)_(yahoo|gtalk|jabber)",file)
            dest = open("logs\\"+name.groups()[2]+".txt","a",encoding="utf-8")
            for line in f.readlines():
                match = re.match('<div class=".+? message" .+? timestamp="(.+?)"><span class="buddy">(.+?)</span> <span class="msgcontent">(<span style=".+?">)?(.+?)</span>',line)
                if match:
                    #print(match.groups())
                    try:
                        dest.write(yaml.dump([match.groups()[0],match.groups()[1],match.groups()[3]], default_flow_style=False,explicit_start=True,allow_unicode=True))
                        count+=1
                    except Exception as e:
                        print("Digsby:")
                        print(e)
                        print(file)
                        print(line)
            dest.close()
        except Exception as e:
            print("Digsby:")
            print(e)
            print(file)