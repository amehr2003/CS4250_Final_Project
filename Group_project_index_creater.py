from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import sys, traceback
import datetime
from sklearn.feature_extraction.text import CountVectorizer
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('wordnet')

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
    docs = col.find()
    for data in docs:
        print(data['_id'])
        term_text = ''
        for row in data['content']:
            print(row)
            term_text += row + '\n'

        my_tokens = do_tokenizing(term_text)
        for term, lemmatized_term in my_tokens:
            print(f"{term} -> {lemmatized_term}")
            save_term_index(db, lemmatized_term, term_text)


def do_tokenizing(input_text):
    # create the transform
    ps = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    # tokenize and lemmatize
    tokens = word_tokenize(input_text)
    lemmatized_tokens = [(token, lemmatizer.lemmatize(token)) for token in tokens if token.isalnum()]

    print(lemmatized_tokens)
    return lemmatized_tokens

def save_term_index(db, term, term_text):
    try:
        ## Collection
        col = db.indexes

        # Create a query to find the document to update
        query = {"term": str(term).strip()}
        doc = col.find_one(query)

        if doc:
            term_list = doc['text']
            term_list.append(term_text)

            # Update the document
            update = {"$set": {"text": term_list}}
            result = col.update_one(query, update)

        else:
            doc = {
                "term": str(term).strip(),
                "text": [term_text],
                "weight": 0
            }
            print(doc)
            result = col.insert_one(doc)

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