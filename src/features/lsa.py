import pickle
import re
from gensim import corpora, models
from gensim.models import lsimodel

__author__ = 'Roland'
import yaml
from collections import defaultdict
from  pprint import pprint
import os
import time
from multiprocessing import Process, Queue,Pool
from Queue import Empty

def useThreads():
    files = os.listdir(folder)
    pool = Pool(processes=7)
    temp = pool.map(parseFile,files)
    results = []
    for t in temp:
        for r in t:
            results.append(r)
    return results

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
    use_pickle = True
    if use_pickle:
        results = useThreads()
        dictionary = corpora.Dictionary(results)
        print(dictionary)
        dictionary.filter_extremes()
        print(dictionary)
        corpus = [dictionary.doc2bow(text) for text in results]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        with open('models//tfidf_corpus.pickle', 'wb') as output:
            pickle.dump(corpus_tfidf, output, pickle.HIGHEST_PROTOCOL)
        with open('models//dictionary.pickle', 'wb') as output:
            pickle.dump(dictionary, output, pickle.HIGHEST_PROTOCOL)
    else:
        with open('models//tfidf_corpus.pickle', 'rb') as input:
            corpus_tfidf = pickle.load(input)
        with open('models//dictionary.pickle', 'rb') as input:
            dictionary = pickle.load(input)
    lsimodel = lsimodel.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=300)
    corpus_lsi = lsimodel[corpus_tfidf]
#    lda = models.ldamodel.LdaModel(corpus=corpus_tfidf, id2word=dictionary, num_topics=300, update_every=1, chunksize=10000, passes=1)
#    lda.save("models//lda.pickle")
    # hdp = models.hdpmodel.HdpModel(corpus_tfidf, id2word=dictionary)
    # hdp.save("models//hdp.pickle")
    # hdp.update_expectations()
    # hdpformatter = models.hdpmodel.HdpTopicFormatter(hdp.id2word,hdp.m_lambda+hdp.m_eta)
    # pprint(hdpformatter.show_topics(topics=-1, topn=20))
    print(time.time() - start_time, "seconds")
