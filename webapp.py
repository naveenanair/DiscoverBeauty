from flask import Flask
from flask import request
from flask import jsonify
import recommender_final
import pickle

app = Flask(__name__)

items = {'cetaphil' : 728, 'mac' : 9246, 'maybelline': 897,
            'benefit' : 114127, 'bobbi' : 591, 'nyx': 111271}

omitWords = ['only', 'untitled', 'other', 'last', 'much', 'first']

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/makemeup/api/v1.0/recommendations/<int:user_id>', methods=['GET'])
def getUserRecommendations(user_id):
    args = request.args
    print args
    return "Hello World! %d" % user_id

@app.route('/makemeup/api/v1.0/recommendations', methods=['GET'])
def getRecommendations():
    products = recommender_final.recoNewUser(request.args)
    results = _getProductDetails(products)
    print results
    return jsonify({ 'recommendations': results })

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def _loadWords():
    f = open('pklfiles/topWords.pkl', 'rb')
    words = pickle.load(f)
    f.close()
    return words

def _getWords(ids):
    global omitWords
    topWords = _loadWords()
    words = []
    for id in ids:
        if id in topWords:
            l = topWords[id]
            words.append([i[0] if i[0] not in omitWords else '' for i in l])
    return words

def _getProductDetails(productsList):
    ids = productsList[1]
    words = _getWords(ids)
    brands = productsList[6]
    categories = productsList[8]
    products = productsList[9]
    return [brands, categories, products, words]

def _getNameToIds(ratingsDict):
    global items
    out = {}
    for name,rating in ratingsDict.iteritems():
        id = items.get(name, None)
        if id:
            out[id] = rating
    return out

if __name__ == "__main__":
    app.run()
