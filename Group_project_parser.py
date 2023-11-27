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

def get_faculty_info_from_db(db):
    ## Collection
    col = db.pages
    docs = col.find()
    for data in docs:
        fac_name = data['name']
        fac_title = data['title']
        fac_phone = data['phone']
        fac_office = data['office']
        fac_email = data['email']
        fac_web = data['web']
        print(fac_name, fac_title, fac_phone, fac_office, fac_email, fac_web, )
        scrap_faculty_individual_page(fac_web)

def scrap_faculty_individual_page(web):
    try:
        html_page = urlopen(web)
    except HTTPError as e:
        print(e)
        # return null, break, or do some other "Plan B"
    else:
        # program continues.
        my_soup = bs(html_page.read(), "html.parser")
        # print(my_soup)
        search_area = my_soup.find_all('div', {"id": "main-body"})
        # print(search_area)
        for search in search_area:
            content_acre = search.find_all('div', {"class": "blurb"})
            for content in content_acre:
                h2 = content.find('h2')
                if h2:
                    print('~~~~~')
                    print(h2.text)

                ps = content.find_all('p')
                print('~~~~~')
                for p in ps:
                    print(p.text)

                ul = content.find('ul')
                if ul:
                    lis = ul.find_all('li')
                    print('~~~~~')
                    for li in lis:
                        print(li.text)


## Initial Infos.
partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

try:
    ## Get Html Content From DB
    get_faculty_info_from_db(db)
    # print(html_page)
except Exception as error:
    traceback.print_exc()
    print("Database not connected successfully")
else:
    print("~~~")
    # program continues.
    # my_soup = bs(html_page, "html.parser")
    # print(my_soup)
