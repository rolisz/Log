__author__ = 'Roland'
import os
import re
from os.path import join, getsize
import yaml
import sys
import urllib.parse
import datetime

fileList = []

for root, dirs, files in os.walk('Trillian'):
    for file in files:
        f = os.path.join(root,file)
        fileName, fileExtension = os.path.splitext(f)
        if fileExtension == '.xml' and fileName[-7:] != "-assets":
            fileList.append(f)
    if '.git' in dirs:
        dirs.remove('.git')  # don't visit CVS directories
    if '.idea' in dirs:
        dirs.remove('.idea')
count = 0

for file in fileList:
    try:
        f = open(file,encoding="utf-8")
        name = re.match("Trillian\\\\logs\\\\(.+?)\\\\Query\\\\(.+?).xml",file)
        dest = open("logs\\"+name.groups()[1]+".txt","a",encoding="utf-8")
        for line in f.readlines():
            match = re.match('<message type=".+?_privateMessage(Offline)?" time="(.+?)" ms=".+?" medium="(.+?)" to=".+?" from="(.+?)" from_display=".+?" text="(.+?)"/>',line)
            if match:
                #print(match.groups())
                try:
                    dest.write(yaml.dump([datetime.datetime.fromtimestamp(int(match.groups()[1])).isoformat(sep=" "),match.groups()[3],urllib.parse.unquote(match.groups()[4])], default_flow_style=False,explicit_start=True,allow_unicode=True))
                    count+=1
                except Exception as e:
                    print(e)
                    print(file)
                    print(line)
        dest.close()
    except Exception as e:
        print(e)
        print(file)

print(count)