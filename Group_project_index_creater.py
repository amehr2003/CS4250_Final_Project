from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import sys, traceback
import datetime
from sklearn.feature_extraction.text import CountVectorizer

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
        print(data['_id'])
        term_text = ''
        for row in data['content']:
            print(row)
            term_text += row + '\n'

        my_token = do_tokenizing(data['content'])
        for term in my_token:
            print(term)
            save_term_index(db, term, term_text)


def do_tokenizing(input):
    # create the transform
    vectorizer = CountVectorizer(stop_words='english')

    # tokenize and build vocab
    vectorizer.fit(input)
    print(vectorizer.vocabulary_)

    voca_dict = vectorizer.vocabulary_
    keys_list = list(voca_dict.keys())
    print(keys_list)

    # encode document
    vector = vectorizer.transform(input)
    print(vector.shape)
    print(vector.toarray())

    return keys_list

def save_term_index(db, term, term_text):
    try:
        ## Collection
        col = db.indexes

        # Create a query to find the document to update
        query = {"term": str(term).strip()}
        doc = col.find_one(query)

        if doc:
            print('Do Update')
            term_list = doc['text']
            term_list.append(term_text)

            # Update the document
            update = {"$set": {"text": term_list}}
            result = col.update_one(query, update)
            print(result)
            print(' has been Updated')

        else:
            print('Do Insert')
            doc = {
                "term": str(term).strip(),
                "text": [term_text],
                "weight": 0
            }
            print(doc)
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been Stored')

        return True
    except Exception as error:
        traceback.print_exc()
        print("Mongo DB Error")
        return False

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
