# Author: Naveena Nair
# Description: Handles data cleaning

from pymongo import MongoClient
import graphlab as gl
import pandas as pd
import numpy as np
from graphlab import SFrame

client = MongoClient()
db = client.makeupalley_main

# Products
################################################################################
def cleanProductsDf(df):
    inputData  = db.products
    products = pd.DataFrame(list(inputData.find()))

    # remove _id column from the DataFrame
    products = products.drop('_id', 1)

    # remove duplicates (yet to be fixed)
    products = products.drop_duplicates()

    # clean
    products['rating'] = products['rating'].astype(float)
    products['buy_again'] = products['buy_again'].str.strip('%')
    products['buy_again'] = products['buy_again'].astype(float)
    products['buy_again'] = products['buy_again'].divide(100)
    products['reviews'] =products['reviews'].str.strip().str.replace(',', '')
    products['reviews'] = products['reviews'].astype(float)

    return products

################################################################################
def cleanAddInfoDf(df):
    inputData  = db.itemadd
    itemadd = pd.DataFrame(list(inputData.find()))

    itemadd = itemadd.drop('_id', 1)
    itemadd['packaging'] = itemadd['packaging'].str.strip().str.replace('Package Quality:', '')
    itemadd['packaging'] = itemadd['packaging'].astype(float)

    itemadd['price'] = itemadd['price'].str.strip().str.replace('Price:', '')
    itemadd['price'] = itemadd['price'].str.strip()
    itemadd['price'].replace(to_replace=["$"], value=["1"], inplace=True, limit=None, regex=False, method='pad', axis=None)
    itemadd['price'].replace(to_replace=["$$"], value=["2"], inplace=True, limit=None, regex=False, method='pad', axis=None)
    itemadd['price'].replace(to_replace=["$$$"], value=["3"], inplace=True, limit=None, regex=False, method='pad', axis=None)
    itemadd['price'].replace(to_replace=["$$$$"], value=["4"], inplace=True, limit=None, regex=False, method='pad', axis=None)
    itemadd['price'] = itemadd['price'].astype(float)

    return itemadd

################################################################################
def cleanReviewsDf(df):
    inputData  = db.reviews
    reviews = pd.DataFrame(list(inputData.find()))

    # remove the _id column
    reviews = reviews.drop('_id', 1)


    # clean user_name
    reviews['user_name'] = reviews['user_name'].apply(lambda x: x.decode('unicode_escape').\
                                              encode('ascii', 'ignore').\
                                              strip())
    # clean rating
    reviews['rating']  = reviews['rating'] .map(lambda x: x[0].split('-')[1])

    # convert rating data into int to pass to data frame
    reviews['rating'] =reviews['rating'].astype(int)

    # clean
    reviews['comments'] = reviews['comments'].str.strip().str.lower().str.replace('_ ', ' ')
    reviews['eyes'] = reviews['eyes'].str.strip().str.lower().str.replace(':', ' ')
    reviews['hair'] = reviews['hair'].str.strip().str.lower().str.replace(':', ' ')
    reviews['skin_type'] = reviews['skin_type'].str.strip().str.lower().str.replace(':', ' ')
    reviews['review_date'] = reviews['review_date'].str.strip().str.replace('on', ' ')
    reviews['age'] = reviews['age'].str.replace(':', ' ')
    reviews['review_date'] = pd.to_datetime(reviews['review_date'])
    reviews[['hair_color', 'hair_type','hair_texture']] = reviews['hair'].str[1:].str.split(',', return_type='frame')
    reviews[['skin_type', 'skin_tone','skin_undertone']] = reviews['skin_type'].str[1:].str.split(',', return_type='frame')
    reviews['skin_type'] = reviews['skin_type'].str.strip()
    reviews = reviews.drop('hair', 1)

    # replacing age values
    reviews[['a', 'b']] = reviews['age'].str[1:].str.split('-', return_type='frame')
    reviews['a'] = reviews['a'].str.replace('18 & Under', '15')
    reviews['a'] = reviews['a'].str.replace('Unknown', '35')
    reviews['a'] = reviews['a'].str.replace('56 & Over', '56')
    reviews['a'] = reviews['a'].astype(int)
    reviews['b'] = reviews['b'].fillna(value=np.nan, inplace=True)
    reviews['b'] = reviews['b'].astype(float)

    reviews['avg_age'] = reviews[['a','b']].mean(axis = 1)
    reviews = reviews.drop('a', 1)
    reviews = reviews.drop('b', 1)
    reviews = reviews.drop('age', 1)

    # dropping duplicates
    reviews = reviews.drop_duplicates()
    return reviews

# reviews - products
# itemadd - products
################################################################################
def merged_dataframe(a, b):
    merged_dataframe = pd.merge(a, b, how='inner', left_on='itemID', right_on='productID',
             left_index=False, right_index=False, sort=True,
             suffixes=('_x', '_y'), copy=True, indicator=False)
    return merged_dataframe

################################################################################
def merged_dataframe2(a, b):
    merged_dataframe = pd.merge(a, b, how='outer', left_on='user_name', right_on='user_name',
             left_index=False, right_index=False, sort=True,
             suffixes=('_x', '_y'), copy=False, indicator=False)
    return merged_dataframe

################################################################################
def merged_dataframe3(a, b):
    merged_dataframe = pd.merge(a, b, how='inner', left_on='itemID', right_on='itemID',
             left_index=False, right_index=False, sort=True,
             suffixes=('_x', '_y'), copy=True, indicator=False)
    return merged_dataframe

################################################################################
def getDummies(df,a):
    for colname in a:
        dummies = pd.get_dummies(df[colname],prefix=colname, prefix_sep='_')
        dColNames = dummies.columns.values.tolist()
        for i in dColNames[1:]:
            df[i] = dummies[i]
    return df
