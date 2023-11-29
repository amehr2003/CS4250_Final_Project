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


def get_faculty_info_from_db(db):
    ## Collection
    col = db.pages
    ## docs = col.find({"name": "Liu, Xin"})
    docs = col.find()
    for data in docs:
        fac_name = data['name']
        fac_title = data['title']
        fac_phone = data['phone']
        fac_office = data['office']
        fac_email = data['email']
        fac_web = data['web']
        # print(fac_name, fac_title, fac_phone, fac_office, fac_email, fac_web, )
        scrap_faculty_individual_page(db, fac_name, fac_title, fac_phone, fac_office, fac_email, fac_web)


def scrap_faculty_individual_page(db, param_name, param_title, param_phone, param_office, param_email, web):
    try:
        html_page = urlopen(web)
    except HTTPError as e:
        print(e)
        # return null, break, or do some other "Plan B"
        return None
    else:
        # program continues.
        my_soup = bs(html_page.read(), "html.parser")
        # print(my_soup)

        schedule_area = my_soup.find_all('span', {"class": "odd"})
        for schedule in schedule_area:
            print(schedule.text)
            param_schedule = schedule.text

        search_area = my_soup.find_all('div', {"id": "main-body"})
        # print(search_area)
        for search in search_area:
            content_area = search.find_all('div', {"class": "blurb"})
            for content in content_area:
                print('==========')
                h2 = content.find('h2')
                if h2:
                    print(h2.text)
                    if h2.text.find('About') >= 0:
                        param_category = 'About'
                    elif h2.text.find('Publications') >= 0:
                        param_category = 'Publication'
                    elif h2.text.find('Honors') >= 0:
                        param_category = 'Honor'
                    elif h2.text.find('Affiliations') >= 0:
                        param_category = 'Affiliation'
                    else:
                        param_category = ''

                param_content = []
                contents = content.find_all('div', {"class": "section-menu"})
                for cont in contents:
                    # print(cont)
                    if cont.find('ol'):
                        print('~~~~~~~~~~~~~~~~~~~~')
                        for ol in content.find_all('ol'):
                            print(ol.find('li').text)
                            param_content.append(ol.find('li').text)

                    elif cont.find('p'):
                        for p in content.find_all('p'):
                            print(p.text)
                            if len(p.text.strip()) > 0:
                                param_content.append(p.text)

                    elif cont.find('ul'):
                        ul = content.find('ul')
                        if ul:
                            lis = ul.find_all('li')
                            for li in lis:
                                print(li.text)
                                if len(li.text.strip()) > 0:
                                    param_content.append(li.text)

                    elif cont.find('span'):
                        print(cont.find('span').text)
                        param_content.append(cont.find('span').text)

                save_document_information(db, param_name, param_title, param_phone, param_office, param_email,
                                          param_schedule, param_category, param_content)

                    # else:
                    #     print(content.text)
                    #     if len(content.text.strip()) > 0:
                    #         param_content.append(content.text)
                    
        return True


def save_document_information(db, pg_name, pg_title, pg_phone, pg_office, pg_email, pg_schedule, pg_category,
                              pg_content):
    try:
        ## Collection
        col = db.documents
        if pg_category != '':
            doc = {
                "name": pg_name,
                "title": pg_title,
                "phone": pg_phone,
                "office": pg_office,
                "email": pg_email,
                "odd": pg_schedule,
                "category": pg_category,
                "content": pg_content
            }
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been Stored')
        else:
            print('SKIP Storing')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


### MongoDB Document Design
'''
document = {
    "_id": {},
    "doc_no": "[Integer Digit]",
    "author": "[String Professor's Name]",
    "title": "[String Professor's Title]",
    "email": "[String Professor's Email]",
    "office": "[String Professor's Office Number]",
    "phone": "[String Professor's Telephone Number]",
    "lecture": "[String Days of Lecture and Time]",
    "catetory": "['AboutMe' or 'SelectedPublication']",
}
'''

## Initial Infos.
partial_url_starter = 'https://www.cpp.edu'

## Get DB Connection
db = connectDataBase()

try:
    ## Get Html Content From DB
    get_faculty_info_from_db(db)
    # print(html_page)
except Exception as error:
    # program error
    traceback.print_exc()
    print("Database not connected successfully")
else:
    # program continue
    print("Continue")
