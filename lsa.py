import re
from gensim import corpora, models
from gensim.models import lsimodel

__author__ = 'Roland'
import yaml
from collections import defaultdict
from  pprint import pprint
import os
import time
from multiprocessing import Process, Queue
from Queue import Empty

def useThreads():
    q = Queue()
    rq = Queue()
    for i in os.listdir(folder)[80:100]:
        q.put(i)
    processes = [Process(target=threadParseFile,args=(q,rq)) for i in range(7)]

    for p in processes:
        p.start()
    results = []
    while not rq.empty() or not q.empty():
        if not rq.empty():
            results.append(rq.get(block=False))
        else:
            time.sleep(5)
    for p in processes:
        print "join"
        p.join()
    while not rq.empty():
        results.append(rq.get(block=False))

def threadParseFile(queue,result_queue):
    i = 0
    while True:
        try:
            file = queue.get(block=False)
            i+=1
            start_time = time.time()
            conversations = parseFile(file)
            for c in conversations:
                result_queue.put(c)
            print(file,time.time() - start_time, "seconds")
        except Empty:
            break
    print("thread done with "+str(i) +" jobs")

def parseFile(file):
    f = open("logs//"+file)
    conversation = []
    for message in yaml.load_all(f.read()):
        reply = message[2].lower().split()
        wordlike = []
        for entity in reply:
            if re.match('[a-zA-Z0-9]',entity):
                wordlike.append(entity)
        conversation.append(wordlike)
    return conversation

if __name__ == '__main__':
    start_time = time.time()

    folder = "logs"

    results = []
    for i in os.listdir(folder)[50:150]:
        for c in parseFile(i):
            results.append(c)

    dictionary = corpora.Dictionary(results)
    print(dictionary)
    dictionary.filter_extremes()
    print(dictionary)
    corpus = [dictionary.doc2bow(text) for text in results]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lsimodel = lsimodel.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    corpus_lsi = lsimodel[corpus_tfidf]
    pprint(lsimodel.show_topics(formatted=True))
    print(time.time() - start_time, "seconds")