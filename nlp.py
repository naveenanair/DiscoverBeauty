# Author: Naveena Nair
# Description: Finding most frequently used adjectives describing products

import datapreprocessing as dp
from pymongo import MongoClient
import graphlab as gl
import pandas as pd
import numpy as np
from graphlab import SFrame
import nltk
import operator
import pickle

################################################################################
def getCommentsPerProduct(comments):
    print "Getting comments per product"
    if comments is None:
        return None

    out = {}
    for id in comments['itemID']:
        j = comments['comments'][comments['itemID'] == id]
        s = []
        for i in  j:
            s.append(i)
        out[id] = s
    return out

################################################################################
def getWords(commentsList):
    print "Getting words"
    words = []
    try:
        for idx,comment in enumerate(commentsList):
            text = nltk.word_tokenize(comment)
            m = nltk.pos_tag(text)
            for i,j in enumerate(m):
                if m[i][1] =="JJ":
                    words.append(m[i][0])
    except TypeError:
        print "TypeError encountered"
    return words

################################################################################
def getWordCounts(words):
    print "Getting word counts"
    counts = {}
    for i in words:
        count = counts.get(i,0)
        counts[i] = count + 1
    return counts

################################################################################
def pickleWords():
    reviews = dp.cleanReviewsDf(1)
    comments = reviews[['itemID','comments']]

    doPickle(comments, "./pklfiles/comments.pkl")

    commentsPerProduct = getCommentsPerProduct(comments)

    wordsPerProduct = {}
    for itemID,commentsList in commentsPerProduct.iteritems():
        words = getWords(commentsList)
        counts = getWordCounts(words)
        sortedWords = sorted(counts.items(), key=operator.itemgetter(1))
        topWords = sortedWords[-10:-1]
        wordsPerProduct[itemID] = topWords
    doPickle(wordsPerProduct, "./pklfiles/topWords.pkl")

################################################################################
def doPickle(obj, filename):
    print "Pickling %s" % filename
    f = open(filename, "w")
    pickle.dump(obj, f)
    f.close()

if __name__ == "__main__":
    pickleWords()
