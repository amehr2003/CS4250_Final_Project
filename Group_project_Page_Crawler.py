from sklearn.feature_extraction.text import TfidfVectorizer
from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import sys, traceback
import datetime

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


def find_target_page_title(partial_url_starter, url_string):
    if url_string.startswith("/cba/international-business-marketing/") or url_string.startswith("/~cba/"):
        url_string = partial_url_starter + url_string

    html_page = urlopen(url_string)
    soup_obj = bs(html_page.read(), "html.parser")
    tag_h1 = soup_obj.find('h1', {"class": "cpp-h1"})

    if tag_h1:
        rtnstr = tag_h1.get_text()
    else:
        rtnstr = ''

    return rtnstr


def save_html_content_db(db, partial_url_starter, url_string, page_title):
    print(url_string)
    col = db.sites
    create_date = datetime.datetime.now()

    if url_string.startswith("/cba/international-business-marketing/") or url_string.startswith("/~cba/"):
        url_string = partial_url_starter + url_string

    html_obj = urlopen(url_string)
    soup = bs(html_obj.read(), "html.parser")
    html_text = soup.find_all('html')
    print(url_string)
    ##print(html_text)

    # Extract text content from the HTML for TF-IDF calculation
    text_content = ' '.join([element.get_text() for element in html_text])

    # Calculate TF-IDF weights using sklearn's TfidfVectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text_content])
    feature_names = vectorizer.get_feature_names_out()

    # Prepare TF-IDF data for storage
    tfidf_data = {}
    for col, term in enumerate(feature_names):
        tfidf_data[term] = tfidf_matrix[0, col]


    doc = {
        "url": str(url_string),
        "title": str(page_title),
        "html": str(html_text),
        "created_at": create_date
    }

    result = col.insert_one(doc)
    print(result.inserted_id)


def append_seeds(partial_url_starter, frontire_list, url_string):
    if url_string in frontire_list:
        print('Already Visited')
    else:
        if url_string.startswith("/cba/international-business-marketing/") or url_string.startswith("/~cba/"):
            url_string = partial_url_starter + url_string
        frontire_list.append(url_string)
    return frontire_list

## Initial Infos.
my_frontier = ['https://www.cpp.edu/cba/international-business-marketing/index.shtml']
partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

## Get Html Content
try:
    html_page = urlopen(my_frontier[0])
except HTTPError as e:
    print(e)
    # return null, break, or do some other "Plan B"
else:
    # program continues.
    my_soup = bs(html_page.read(), "html.parser")
    # print(my_soup)
    all_links = my_soup.find_all('a', {})
    link_cnt = 0
    for link in all_links:
        inner_link = link.get("href")
        # print(inner_link)
        if str(inner_link).startswith("/cba/international-business-marketing/") or str(inner_link).startswith("/~cba") or str(inner_link).startswith("http"):
            my_frontier = append_seeds(partial_url_starter, my_frontier, inner_link)
            print(my_frontier)
            title = find_target_page_title(partial_url_starter, inner_link)
            print(title)
            save_html_content_db(db, partial_url_starter, inner_link, title)
            print("Page Saved...")
            if str(title) == 'Faculty & Staff Directory':
                print("STOP Here")
                # remove all elements from frontier
                my_frontier.clear()
                break
            link_cnt += 1
            print(link_cnt)
