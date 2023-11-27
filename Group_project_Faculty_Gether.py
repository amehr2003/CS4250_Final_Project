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

def save_html_information(db, pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web):
    try:
        ## Collection
        col = db.pages
        if pf_name != '':
            doc = {
                "name": pf_name,
                "title": pf_title,
                "phone": pf_phone,
                "office": pf_office,
                "email": pf_email,
                "web": pf_web
            }
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been Stored')
        else:
            print('SKIP Storing')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False

def get_target_page(db):
    try:
        ## Collection
        col = db.sites
        ## Find Page
        pipeline = [
            {'$match': {'title': 'Faculty & Staff Directory'}}
        ]
        ## Query
        docs = col.aggregate(pipeline)
        for data in docs:
            html_source = data['html']
        return html_source
    except Exception as error:
        print("Mongo DB Error")
        return None

## Initial Infos.
partial_url_starter = 'https://www.cpp.edu'
num_targets = 10

## Get DB Connection
db = connectDataBase()

try:
    ## Get Html Content From DB
    html_page = get_target_page(db)
    # print(html_page)
except Exception as error:
    traceback.print_exc()
    print("Database not connected successfully")
else:
    # program continues.
    my_soup = bs(html_page, "html.parser")
    # print(my_soup)
    all_prof = my_soup.find_all('div', {"class": "card-body d-flex flex-column align-items-start"})
    print("======================================================================================")
    targets_found = 0

    for prof in all_prof:
        pf_name = pf_title = pf_office = pf_phone = pf_email = pf_web = ''
        prof_name = prof.find_all('h3', {"class": "mb-0"})
        for name in prof_name:
            # print(name.get_text().strip())
            pf_name = name.get_text().strip()
        prof_title = prof.find_all('div', {"class": "mb-1 text-muted"})
        for title in prof_title:
            # print(title.get_text().strip())
            pf_title = title.get_text().strip()
        prof_info = prof.find_all('ul', {})
        for info in prof_info:
            for i, info in enumerate(info.find_all('li')):
                if i == 0:
                    # print(info.get_text().replace('phone number or extension', ''))
                    pf_phone = info.get_text().replace('phone number or extension', '')
                if i == 1:
                    # print(info.get_text().replace('office location', ''))
                    pf_office = info.get_text().replace('office location', '')
                if i == 2:
                    # print(info.find('a').get('href').replace('mailto:', ''))
                    pf_email = info.find('a').get('href').replace('mailto:', '')
                if i == 3:
                    # print(partial_url_starter + str(info.find('a').get('href')))
                    pf_web = partial_url_starter + str(info.find('a').get('href'))
        if targets_found < num_targets:
            print(pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web)
            db_result = save_html_information(db, pf_name, pf_title, pf_office, pf_phone, pf_email, pf_web)
            print(db_result)
            targets_found += 1
        else:
            print('Stop Gethering')
            break

