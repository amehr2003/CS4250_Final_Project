from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import pymongo
import traceback

nltk.download('punkt')
nltk.download('wordnet')


def connectDataBase():
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

    # Display results
    for result in paginated_results:
        print(result)


if __name__ == "__main__":
    main()
