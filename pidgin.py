__author__ = 'Roland'
import os
import re
from os.path import join, getsize
import yaml
import sys

def parse(folder = "Pidgin"):
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
            name = re.match("Pidgin\\\\logs\\\\.+?\\\\rolisz(.+?)?\\\\(.+?)\\\\(\d\d\d\d-\d\d-\d\d)(.+?)\.html",file)
            dest = open("logs\\"+name.groups()[1]+".txt","a",encoding="utf-8")
            for line in f.readlines():
                match = re.match('<font color=".+?"><font size="2">\((\d\d:\d\d\:\d\d [AP]M)\)</font> <b>(.+?)</b></font>(.+?)<br/>',line)
                if match:
                    #print(match.groups())
                    try:
                        dest.write(yaml.dump([name.groups()[2]+" "+match.groups()[0],match.groups()[1],match.groups()[2]], default_flow_style=False,explicit_start=True,allow_unicode=True))
                        count+=1
                    except Exception as e:
                        print("Pidgin:")
                        print(e)
                        print(file)
                        print(line)
            dest.close()
        except Exception as e:
            print("Pidgin:")
            print(e)
            print(file)