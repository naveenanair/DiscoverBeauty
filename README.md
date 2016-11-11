
## Discover Beauty 
***
Galvanize Capstone Project - October 2016 

## Overview
***
Cosmetic products are used by everyone! Discover beauty is a recommender that generates personalized cosmetic recommendations for you based on your unique requirements. It also provides context rich recommendations by which you can know more about the products specifically recommender for you! 

## Data
***
All data to build the recommender was scrapped from makeupalley.com. makeupalley.com is an authoritative resource for cosmetic product reviews. It has a dedicated community of users committed to exploring and providing accurate feedback on their experiences with various cosmetic products. 
The following information was scrapped and stored in a Mongoldb database:
* Products: Attributes included productID, name, brand, category, price, packaging, overall rating, number of reviews, %buyagain.
* Reviews: Attributes included productID, userID, user rating, review, user age, and other features about the user such as hair color, eye color etc.

## Data Pipeline 
***
### Matrix Factorization 
After the initial data exploration, I concluded that key user characteristics such as age and product characteristics such as packaging needed to be included in my recommender. To build the recommender, I used Graphlab, a neat package that allows you to build and evaluate recommendation systems. Graphlab integrates seamlessly with pandas, enabling data manipulation in pandas and building the model in graphlab.
I used a factorization recommender to build my product as I wanted the model to pick up on latent user features.

### Cosine Similarity 
Graphlab has in-built functions that can be used to generate predictions for new users. I tried using this function with a new observation set of ratings for new users. However, due to matrix sparsity and cold start issues, the recommender would always spit out the most popular products irrespective of the user interaction data entered. I therefore, appended my model with a cosine similarity model.
For the cosine similarity model I used new user characteristics such as age, skin tone etc, and then leveraged existing user metadata and cosine similarity to find an existing user most similar to the new user. I then generated recommendation results of the closest existing user.
This makes intuitive: users that have a certain characteristic for eg. acne prone skin, would like to buy products that similar users have procured. This also saved a lot of time as I did not have to rerun the model. I pickled the recommender results, user and product information tables, and leveraged them in the script to generate recommendations.

### Word Tagging 
I also used the product review to add additional context to recommendations. I used word tagging to tag description words or adjectives used to describe products in the reviews eg. words like natural or dry were selected. I then aggregated the ten most frequently occurring description words for each item. 

##  Repo structure 
***
* Model
- recommender.py
- run.py
- nlp.py
* Scraper
- datapreprocessing.py
- dbhelper.py
- webscraper.py
* Webapp
- webapp.py
- discover.html

##  Future work 
***
Build a color base of makeup products , allow user to ender favorite lipstick color and generate cost effective recommendations. 

##  Packages used 
***
* NumPy
* pandas
* scikit-learn
* Graphlab
* NLTK
* urllib
* BeautifulSoup
* PyMongo
* Flask
* Tableau
