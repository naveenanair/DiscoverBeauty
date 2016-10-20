# Author: Naveena Nair
# Description: Builds data pipeline and creates recommender models

import datapreprocessing as dp
from pymongo import MongoClient
import graphlab as gl
import pandas as pd
import numpy as np
from graphlab import SFrame

# Pipeline
################################################################################
products = dp.cleanProductsDf(1)
products = products.drop(products.index[products.duplicated(subset = 'productID')])
itemadd = dp.cleanAddInfoDf(1)
reviews = dp.cleanReviewsDf(1)

overall_products = dp.merged_dataframe(itemadd, products)
dummies_reqd = ['brand','category']
updated_products = dp.getDummies(overall_products, dummies_reqd) #verify all fields are int /float
updated_products = updated_products.drop(['productID','url','categoryID'],1) #[itemID,reviews,packaging,price,rating + brand dummies + category dummies ]

user_info = reviews[['user_name','eyes','skin_type','skin_tone','skin_undertone','avg_age','hair_color','hair_type','hair_texture']]
user_info = user_info.drop(user_info.index[user_info.duplicated(subset = 'user_name')])
user_info['userID'] = np.arange(0,len(user_info),1)

action = reviews [['itemID', 'rating','user_name']]
user_dum =['eyes','skin_type','skin_tone','skin_undertone','hair_color','hair_type','hair_texture']
upuser_info = dp.getDummies(user_info,user_dum)

upuser_info = upuser_info.drop(['eyes','skin_type','skin_tone','skin_undertone','avg_age','hair_color','hair_type','hair_texture'],1)
merged_action = dp.merged_dataframe2(action,upuser_info)


final_action = merged_action[['itemID', 'rating','userID']]
final_user = upuser_info
final_item = updated_products

# Graphlab
################################################################################
users = gl.SFrame(final_user)
items = gl.SFrame(final_item)
actions = gl.SFrame(final_action)

model  = gl.recommender.factorization_recommender.create(actions,
user_id='userID', item_id='itemID',
target='rating', user_data=users,
item_data=items, num_factors=8, regularization=1e-08,
linear_regularization=1e-10, side_data_factorization=True,
nmf=False, binary_target=False, max_iterations=50, sgd_step_size=0, random_seed=0, solver='als', verbose=True)
rec = model.recommend()
results_df = gl.SFrame.to_dataframe(rec)

display_df = dp.merged_dataframe3(results_df, updated_products)[['userID','itemID',
'score','rank','packaging','price','brand','buy_again','category','name']]

final_rec = display_df[display_df.name.str.contains("DISCONTINUED") == False]


# Cosine similarity
################################################################################

# ------------------------------------------------------------------------------
# Code to take user from wed app <<This code needs to come after reviews df is created>>
# dColNames = reviews.columns.values.tolist()
# webip =websiteinput in the form of a numpy array having the following columns
# [u'comments',
#  u'eyes',
#  u'itemID',
#  u'rating',
#  u'review_date',
#  u'skin_type',
#  u'user_name',
#  'hair_color',
#  'hair_type',
#  'hair_texture',
#  'skin_tone',
#  'skin_undertone',
#   'avg_age']
# df = pd.DataFrame(webip, columns=dColNames)


# # --------------------------------------------------------------------------
# # factorization recommender with side data
# model  = gl.recommender.factorization_recommender.create(actions,
# user_id='userID', item_id='itemID',
# target='rating', user_data=user,
# item_data=item, num_factors=8, regularization=1e-08,
# linear_regularization=1e-10, side_data_factorization=True,
# nmf=False, binary_target=False, max_iterations=50, sgd_step_size=0, random_seed=0, solver='als', verbose=True)
# results = model.recommend()
#
# # --------------------------------------------------------------------------
#
# results_df = gl.SFrame.to_dataframe(results)
# #combine results with items tables to understand what products are recommended for what user
# combined_results = dp.merged_dataframe3(results_df,updated_products)
# abridged_cr = combined_results[['userID','itemID','score','rank','packaging','price','brand','buy_again','category','name','reviews','rating']]
# # --------------------------------------------------------------------------
# print abridged_cr['userID'].value_counts()


#item similarity model

# training_data, validation_data = gl.recommender.util.random_split_by_user(action, 'userID', 'itemID')
# model = gl.recommender.create(training_data, 'userID', 'itemID', target = 'rating')
# results = model.recommend()
#
# similar_items = model.get_similar_items(action['itemID'], k=2)
# view = model.views.overview(validation_set=validation_data,
#                             user_data=user,
#                             user_name_column='userID',
#                             item_data=item,
#                             item_name_column='itemID')

# --------------------------------------------------------------------------
#item content recommender

# model = gl.recommender.item_content_recommender.create(item,
# item_id ='itemID', observation_data=training_data, user_id='userID',
# target='rating', weights='auto', similarity_metrics='auto', item_data_transform='auto',
# max_item_neighborhood_size=64, verbose=True) #item content model

# --------------------------------------------------------------------------
# factorization recommender with no side data
# model2 = gl.recommender.factorization_recommender.create(
#             training_data,
#             user_id='userID',
#             item_id='itemID',
#             target='rating',
#             solver='als',
#             side_data_factorization=False)
# --------------------------------------------------------------------------
# # factorization recommender with side data
# model  = gl.recommender.factorization_recommender.create(training_data,
# user_id='userID', item_id='itemID',
# target='rating', user_data=user,
# item_data=item, num_factors=8, regularization=1e-08,
# linear_regularization=1e-10, side_data_factorization=True,
# nmf=False, binary_target=False, max_iterations=50, sgd_step_size=0, random_seed=0, solver='als', verbose=True)
# results = model.recommend()
# combined_results = merged_dataframe(results_df,updated_products)
# abridged_cr = combined_results[['userID','itemID','score','rank','packaging','price','brand','buy_again','category','name','reviews','rating']]
# --------------------------------------------------------------------------
#baseline popularity recommender with side data

# model4 = gl.recommender.popularity_recommender.create(training_data,
# user_id='userID', item_id='itemID',
#  target='rating', user_data=user,
#  item_data=item, random_seed=0,
#  verbose=True)
