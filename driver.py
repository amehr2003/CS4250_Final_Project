from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import pymongo
import traceback


def connectDataBase():
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        print("database connected successfully...")
        db = client.cs4250prj
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully")


def preprocess_text_data(texts):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(texts)
    return tfidf_matrix, vectorizer


# vectorization and cosine_sim checking
def search_engine(query, tfidf_matrix, documents, vectorizer):
    query_vector = vectorizer.transform([query])
    # 1-D array of similarity scores
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
    # Descending order for best results
    sorted_results = similarities.argsort()[::-1]
    sorted_documents = [documents[i] for i in sorted_results]
    return sorted_documents


def paginate_results(results, page_number, items_per_page=5):
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page
    return results[start_index:end_index]


# Cut the text field off after 160 characters
def cut_string_short(string):
    string = str(string)
    i = 0
    returnString = ""
    while i < len(string):
        if i == 75 or i == 150 or i == 225:
            returnString += "\n"
        returnString += string[i]
        i += 1
        if i > 300:
            returnString += "... \n"
            break
    return returnString


def clean_up_results(dic):
    url = None
    text_list = dic.get('text', [{'text': 'N/A'}])
    for entry in text_list:
        if 'url' in entry:
            url = entry['url']
            break
    url = url or 'N/A'
    text = "\n".join(entry.get('text', 'N/A') for entry in text_list)
    print(f"URL: {url}\n"
          f"Text: {cut_string_short(text)}")


def main():
    db = connectDataBase()

    # Retrieve data from MongoDB
    collection = db['indexes']
    documents = list(collection.find())

    # Preprocess text data
    texts = [doc['term'] for doc in documents]
    tfidf_matrix, vectorizer = preprocess_text_data(texts)

    # User input for the query and page number
    user_query = input("Enter your query: ")
    page_number = int(input("Enter which page of results(enter '1' for best results): "))

    # Search and paginate results
    results = search_engine(user_query, tfidf_matrix, documents, vectorizer)
    paginated_results = paginate_results(results, page_number)

    for result in paginated_results:
        clean_up_results(result)


if __name__ == "__main__":
    main()
