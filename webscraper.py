# Author: Naveena Nair
# Description: Scrapes website to gather makeup data

import requests
from requests.packages.urllib3 import add_stderr_logger
from bs4 import BeautifulSoup
import urllib2
import login
import re
import requests
from pymongo import MongoClient
import dbhelper
import pymongo, json
import bson

################################################################################
def getHTML(url):
    if url is None:
        return None
    html = urllib2.urlopen(url).read()
    return html

################################################################################
def getSoup(url):
    if url is None:
        return None
    html = urllib2.urlopen(url)
    return BeautifulSoup(html)

################################################################################
def getReviewsByProduct(ids):
    for prodID in ids:
        pageList = getReviewsPages(prodID)
        for htmlPage in pageList:
            parseAndStoreReviews(prodID, htmlPage)

################################################################################
def getReviewsPages(prodID):
    pageList = []
    client = MongoClient()
    db = client.rawmakeupalley
    cursor = db.reviews.find({"productID": prodID})
    for doc in cursor:
        html = str(doc['html'])
        pageList.append(html)
    return pageList

################################################################################
def parseAndStoreReviews(prodID, htmlStr):
    soup = BeautifulSoup(htmlStr)
    m = soup.find_all('div', attrs={'id':'reviews-wrapper'})

    if len(m) == 0:
        return None

    rrows = m[0].find_all('div', attrs={'class':'comments'})
    reviews = []
    for i in rrows:
        review_heading =  i.find_all('div', attrs={'class':'comment-heading'})

        rating_data = i.find_all('div', attrs={'class':'lipies'})
        rating = rating_data[0].span['class']

        user_det = i.find_all('div', attrs={'class':'user-name'})
        user_name  = user_det[0].p.a.string

        review_content =  i.find_all('p', attrs={'class':'break-word'})
        if len(review_content) == 0:
            review_content =  i.find_all('p', attrs={'class':'1break-word'})
        comments = None
        try:
            comments = review_content[0].contents[0]
        except IndexError:
            print review_content
            print review_content[0].contents
        rd = i.find_all('div', attrs={'class':'date'})
        review_date = rd[0].p.get_text()
        user_attrs1 = None
        try:
            user_attrs = i.find_all('div', attrs={'class':'important'})
            user_attrs1 = user_attrs[0].find_all('p')
            age = user_attrs1[0].contents[1]
            skin_type = user_attrs1[1].contents[1]
            hair = user_attrs1[2].contents[1]
            eyes = user_attrs1[3].contents[1]
            writeReviewsToDb({prodID : [(prodID, rating, user_name,age,skin_type,hair,eyes,review_date,comments)]})
        except IndexError:
            print "Error reading reviews for product", prodID
    return reviews

################################################################################
def getProductsPerCategory(ids):
    catalogue = {}
    for catID in ids:
        pageList = getProductPages(catID)
        results = []
        for htmlPage in pageList:
            result = getProducts(catID, htmlPage)
            if result is None:
                continue
            results.extend(result)
        catalogue[catID] = results
    return catalogue

################################################################################
def getProductPages(catID):
    pageList = []
    client = MongoClient()
    db = client.rawmakeupalley
    cursor = db.products.find({"categoryID": catID})
    for doc in cursor:
        html = str(doc['html'])
        pageList.append(html)
    return pageList

################################################################################
def storeProductsPerCategory(ids):
    for catID in ids:
        storeAllPages(catID, storeProducts)

################################################################################
def storeReviewsPerProduct(ids):
    for prodID in ids:
        print "Getting reviews for product %d" % prodID
        storeAllPages(prodID, storeReviews)

################################################################################
def getAllPages(id, func, getResults=True):
        i = 1
        results = [] if getResults else None
        while True:
            pageResult = func(id, i)
            if pageResult is None:
                break
            i +=1
            if results is not None:
                results.extend(pageResult)
        return results

################################################################################
def storeAllPages(id, func):
    return getAllPages(id, func, False)

################################################################################
def storeProducts(categoryID, page=1):
    url = "https://www.makeupalley.com/product/searching.asp/page=%d/pagesize=15/CategoryId=%s/NumberOfReviews=250/" % (page,categoryID)
    html = getHTML(url)
    soup = getSoup(url)
    m = soup.find_all('table', attrs={'class':"table"})
    if len(m) == 0:
        return None

    client = MongoClient()
    db = client.rawmakeupalley
    db.products.insert({"categoryID": categoryID, "html": bson.Binary(str(html))})
    return html

################################################################################
def storeReviews(productID, page=1):
    print "Storing reviews for ", productID, page
    url = "https://www.makeupalley.com/product/showreview.asp/page=%d/pagesize=10/ItemID=%d/"%(page,productID)
    html = getHTML(url)
    soup = getSoup(url)
    m = soup.find_all('div', attrs={'id':'reviews-wrapper'})
    if len(m) == 0:
        return None

    client = MongoClient()
    db = client.rawmakeupalley
    db.reviews.insert({"productID": productID, "html": bson.Binary(str(html))})
    return html

################################################################################
def getProducts(categoryID, htmlStr):
    soup = BeautifulSoup(htmlStr)
    m = soup.find_all('table', attrs={'class':"table"})
    if len(m) == 0:
        return None
    trows = m[0].find_all('tr')
    products =[]
    itemIDs = []

    for i in trows[1:]:
        product_det =  i.find_all('td')
        brand = product_det[0].contents[0]
        product = product_det[1].find_all('a')
        productUrl = product[0]['href']
        itemID = int(re.search(r'\d+', productUrl).group())
        productDesc = product[0].contents[2]
        category = product_det[2].contents[0]
        rating = product_det[3].contents[0]
        numReviews = product_det[4].contents[0]
        buyAgain = product_det[5].contents[0]
        products.append((brand, productUrl, itemID, productDesc, category,
                                                rating, numReviews, buyAgain))
    return products

################################################################################
def getProductIDs(productsPerCategory):
    productIDs = []
    for catID in productsPerCategory:
        products = productsPerCategory[catID]
        ids = [x[2] for x in products]
        productIDs.extend(ids)
    return set(productIDs)

################################################################################
def writeProductsToDb(productsPerCategory):
    db, colls = dbhelper.init_mongo_client('makeupalley_main')
    for catID, productsList in productsPerCategory.iteritems():
        for x in productsList:
            try:
                dbhelper.insertRow(db, 'products', \
                    {'categoryID': catID, 'productID': x[2], 'name': x[3], 'brand': x[0], 'url' : x[1],
                        'category': x[4], 'rating': x[5], 'reviews': x[6],
                            'buy_again': x[7]})
            except IndexError:
                print "IndexError", x

################################################################################
def writeReviewsToDb(reviewsPerProduct):
    #itemID, rating, user_name,age,skin_type,hair,eyes,review_date,comments

    print "Storing reviews for", reviewsPerProduct.keys()

    db, colls = dbhelper.init_mongo_client('makeupalley_main')
    for reviews in reviewsPerProduct.values():
        for item_ID, rating, user_name,age,skin_type,hair,eyes,review_date,comments in reviews:
            dbhelper.insertRow(db, 'reviews', \
                {'itemID': item_ID, 'rating': rating, 'user_name' : user_name,
                    'age' : age, 'skin_type' : skin_type, 'hair': hair,
                    'eyes': eyes,'review_date' : review_date,'comments' : comments})

################################################################################
def getDistinctProductIDs():
    db, colls = dbhelper.init_mongo_client('makeupalley_main')
    allProductIDs = db.products.distinct('productID')
    return allProductIDs

################################################################################
def fixMissingReviews():
    ids = getDistinctProductIDs()
    getReviewsByProduct(ids)

################################################################################
def getCategoryIDs():
    categoryIDs = [4, 102, 201, 502, 701]
    return categoryIDs

################################################################################
if __name__ == "__main__":
    categoryIDs = getCategoryIDs()
    storeProductsPerCategory(categoryIDs)

    productsPerCategory = getProductsPerCategory(categoryIDs)
    writeProductsToDb(productsPerCategory)

    productIDs = getProductIDs(productsPerCategory)
    storeReviewsPerProduct(productIDs)

    getReviewsByProduct(productIDs)
