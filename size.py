__author__ = 'Roland'
import yaml
from collections import defaultdict
import pprint
import datetime
import os
import time
from multiprocessing import Process, Queue
from Queue import Empty

def parseFile(queue,result_queue):
    while True:
        try:
            file = queue.get(block=False)
            start_time = time.time()
            f = open("logs//"+file,encoding="utf-8")
            me = defaultdict(lambda: 0)
            other = defaultdict(lambda: 0)
            for message in yaml.load_all(f.read()):
                try:
                    date = datetime.datetime.strptime(message[0],"%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    try:
                        date = datetime.datetime.strptime(message[0],"%Y-%m-%d %H:%M:%S %p")
                    except ValueError as e:
                        print("This one ain't good: "+message[0])
                        continue
                if message[1] == file[:-4]:
                    other[date.strftime("%Y-%m-%d")] += len(message[2])
                else:
                    me[date.strftime("%Y-%m-%d")] += len(message[2])
            days = len(me) if len(me) else len(other)
            meCount = sum(me.values())
            otherCount = sum(other.values())
            ratio = meCount/otherCount if otherCount else 'Inf'
            result_queue.put((file,days,meCount,otherCount,ratio))
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
    results = []
    while not rq.empty() or not q.empty():
        if not rq.empty():
            results.append(rq.get(block=False))
        else:
            time.sleep(5)
    for p in processes:
        p.join()
    while not rq.empty():
        results.append(rq.get(block=False))
    pprint.pprint(results,width=200)

    print(time.time() - start_time, "seconds")
