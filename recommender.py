# Author: Naveena Nair
# Description: Provides recommendations for new users

import datapreprocessing as dp
from pymongo import MongoClient
import graphlab as gl
import pandas as pd
import numpy as np
from graphlab import SFrame
from sklearn.metrics.pairwise import linear_kernel
import pickle

################################################################################
def recoNewUser(dit):#dict of user char
    # my_model = gl.load_model('/Users/naveenanair/Project/model_addedage')
    results = loadPkl("/Users/naveenanair/Project/pklfiles/results.pkl")
    final_user = loadPkl("/Users/naveenanair/Project/pklfiles/finalUser.pkl")
    cols = final_user.columns.values.tolist()

    updated_products = loadPkl("/Users/naveenanair/Project/pklfiles/updated_products.pkl")

    newUserChar = {}
    for i in cols:
        newUserChar[i] = 0
    for key,value in dit.iteritems():
        if key in dit:
            newUserChar[key] = int(value)

    df = final_user.head(1)
    for i in cols:
        df[i] = newUserChar[i]

    df = df.values[:,5:]
    df = np.delete(df, [1,2,3,4], 1)

    x = final_user.values[:,5:]
    x = np.delete(x, [1,2,3,4], 1)

    cosine_similarities = linear_kernel(df, x)
    index = np.argmin(cosine_similarities)
    newUserReco = results [results['userID'] == final_user.values[index][9]]

    display_df = dp.merged_dataframe3(newUserReco, updated_products)[['userID','itemID',
            'score','rank','packaging','price','brand','buy_again','category','name']]

    final_rec = display_df[display_df.name.str.contains("DISCONTINUED") == False]
    return final_rec.values.T.tolist()

################################################################################
def loadPkl(filename):
    f = open(filename, "r")
    obj = pickle.load(f)
    f.close()
    return obj
