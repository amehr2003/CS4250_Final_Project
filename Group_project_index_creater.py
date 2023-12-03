from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import sys, traceback
import datetime
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from collections import OrderedDict

## functions
def connectDataBase():
    # Create a database connection object using pymongo
    # --> add your Python code here
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        print("---Client---")
        print(client)
        db = client.cs4250prj
        print("---DB---")
        print(db)
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully")


def get_faculty_page_from_db(db):
    ## Collection
    col = db.documents
    docs = col.find({"name": "Bryant, Frank K."})
    for data in docs:
        for row in data['content']:
            do_tokenizing([row], data['_id'])

def do_tokenizing(input, doc_id):
    print("===== Document ID & TEXT =====")
    print(doc_id)
    print(input)
    # create token
    ps = PorterStemmer()
    vectorizer = CountVectorizer(stop_words='english')

    # tokenize and build voca
    vectorizer.fit(input)
    print("--- Do Stopping ---")
    print(vectorizer.vocabulary_)

    voca_dict = vectorizer.vocabulary_
    term_positions = {key: i for i, key in enumerate(voca_dict)}
    print("--- Term Postion Dict ---")
    print(term_positions)
    '''
    for x in term_positions:
        print(x)
    '''

    sorted_dict = OrderedDict(sorted(voca_dict.items(), key=lambda item: item[1], reverse=False))
    print("--- Sorting Terms by Index ---")
    print(sorted_dict)

    # encode document
    vector = vectorizer.transform(input)
    print("--- Vector Shape ---")
    print(vector.shape)

    print("--- Vector: Term Counts ---")
    # print(vector.toarray())
    list = vector.toarray()
    for count in list:
        print(count)
        term_counts = count

    wnl = WordNetLemmatizer()
    # Lemmatizing trial
    print("--- Lemmatizing ---")
    print("{0:20}{1:20}".format("--Word--", "--Lemma--"))
    for i, word in enumerate(sorted_dict):
        print("{0:20}{1:20}".format(word, wnl.lemmatize(word, pos="v")))
        term = str(wnl.lemmatize(word, pos="v")).strip()
        term_count = term_counts[i]
        term_postion = get_position(word, term_positions)

        ## Store Term into DB
        save_term_index(db, term, term_count, term_postion, doc_id)


def save_term_index(db, term, term_count, term_postion, doc_id):
    try:
        ## Collection
        col = db.indexes

        # Create a query to find the document to update
        pipeline = [
                {
                    '$match': {
                        'term': str(term),
                        'doc.doc_id': 'ObjectId('+str(doc_id)+')'
                    }
                },
                {
                    '$project': {'countFromNestedArray': '$doc.count'}
                }
        ]
        doc = col.aggregate(pipeline)
        print(doc)

        if doc:
            print('Do Update')
            # term_list = doc['text']
            # term_list.append(term_text)

            # update = {"$set": {"text": term_list}}
            # result = col.update_one(query, update)
            # print(result)
            print(' has been Updated')

        else:
            print('Do Insert')
            doc = {
                "term": str(term).strip(),
                "doc": [
                        {
                            "doc_id": doc_id,
                            "position": int(term_postion),
                            "count": int(term_count)
                        }
                ],
            }
            print(doc)
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been Stored')

        return True
    except Exception as error:
        traceback.print_exc()
        print("Mongo DB Error")
        return False

def get_position(term, term_position_dict):
    position = 0
    for index, value in enumerate(term_position_dict):
        if str(value) == str(term):
            position = index
            break
    return position


### MongoDB Document Design
'''
index = {
    "_id": {},
    "term": "[lemmatized token from document]",
    "doc_txt": "[docuement text]"
    "title": "[String Professor's Title]",

}
'''


## Initial Infos.
partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

try:
    ## Get Html Content From DB
    get_faculty_page_from_db(db)
    # print(html_page)
except Exception as error:
    # program error
    traceback.print_exc()
    print("Database not connected successfully")
else:
    # program continue
    print("Continue")

