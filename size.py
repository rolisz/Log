__author__ = 'Roland'
import yaml
from collections import defaultdict
import pprint
import datetime
import os
import time
from multiprocessing import Process, Queue
from queue import Empty

def parseFile(queue,result_queue):
    while True:
        try:
            file = queue.get(block=False)
            start_time = time.time()
            f = open("logs//"+file,encoding="utf-8")
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
            result_queue.put((file,len(size),sum(size.values())))
            print(file,time.time() - start_time, "seconds")
        except Empty:
            break
    print("thread done")

if __name__ == '__main__':
    start_time = time.time()

    folder = "logs"

    q = Queue()
    rq = Queue()
    for i in os.listdir("logs"):
        q.put(i)
    processes = [Process(target=parseFile,args=(q,rq)) for i in range(7)]

    for p in processes:
        p.start()
    print("started")
    while not rq.empty() or not q.empty():
        if not rq.empty():
            print("smt")
            print(rq.get(block=False))
        else:
            time.sleep(5)
    for p in processes:
        p.join()
        print("joined")
    print("Size:")


    print(time.time() - start_time, "seconds")