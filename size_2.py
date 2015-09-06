__author__ = 'Roland'
import yaml
from collections import defaultdict
import pprint
import datetime
import os
import time
import threading
import Queue

start_time = time.time()

folder = "logs"
discussions = []

class fileThread(threading.Thread):

    def __init__(self,file):
        self.file = file
        self.result = []
        threading.Thread.__init__(self)

    def run(self):
        f = open("logs//"+self.file,encoding="utf-8")
        size = defaultdict(lambda: 0)
        for message in yaml.load_all(f.read()):
            try:
                date = datetime.datetime.strptime(message[0],"%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                try:
                    date = datetime.datetime.strptime(message[0],"%Y-%m-%d %H:%M:%S %p")
                except ValueError as e:
                    print("This one ain't good: "+message[0])
                    continue
            size[date.strftime("%Y-%m-%d")] += len(message[2])
        self.result = (self.file,len(size),sum(size.values()))
        print(self.file)

    def get_result(self):
        return self.result



def producer(q, files):
    for file in files:
        thread = fileThread(file)
        thread.start()
        q.put(thread, True)

finished = []
def consumer(q, total_files):
    while len(finished) < total_files:
        thread = q.get(True)
        thread.join()
        finished.append(thread.get_result())

q = Queue.Queue(20)
files = os.listdir("logs")
prod_thread = threading.Thread(target=producer, args=(q, files))
cons_thread = threading.Thread(target=consumer, args=(q, len(files)))
prod_thread.start()
cons_thread.start()
prod_thread.join()
cons_thread.join()

print("Size:")
pprint.pprint(finished)

print(time.time() - start_time, "seconds")
