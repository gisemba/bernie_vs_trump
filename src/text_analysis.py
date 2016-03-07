import nltk
import string
import sklearn
import json
from sklearn.feature_extraction.text import TfidfVectorizer

""" This program analyzes the texts we collected using the bag-of-words (BoW) approach. We
    treat each set of texts (e.g. Tweets made by Trump) as a BoW by combining
    them all together. We then compare these BoW to assess the similarity between each set.

    (1) We use NLTK and string methods to clean up the data and simplify
    the strings to make a BoW.
    (2) After constructing each BoW we use scikit-learn to represent the BoW as a
    numerical vector using TF-IDF weighting.
    (3) We compute the cosine similarity scores of each vector to assess their similarity.
    """

#RESOURCES USED:
#GENEAL INFO: http://stackoverflow.com/questions/8897593/similarity-between-two-text-documents
#ON COSINE SIMILARIY: http://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html,
#http://stackoverflow.com/questions/12118720/python-tf-idf-cosine-to-find-document-similarity
#TF-IDF WEIGHTS: http://nlp.stanford.edu/IR-book/html/htmledition/tf-idf-weighting-1.html



"""Takes a string, converts it to lowercase and removes punctuation.
    Returns a the edited string"""
def Preprocess(S):
    #Coverts uppercase to lower
    S = S.lower()
    #Removes all punctuation
    punct = set(string.punctuation)
    S = ''.join(ch for ch in S if ch not in punct)
    return S

#Setting the stemmer
stemmer = nltk.stem.porter.PorterStemmer()

"""Takes a string, tokenizes the string and stems the tokens.
    Returns a list of stems"""
def Tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = [stemmer.stem(t) for t in tokens]
    return stems

#Setting the vectorizer
vectorizer = TfidfVectorizer(tokenizer=Tokenize, stop_words='english')

"""Converts each string into a TF-IDF weighted numerical vector.
    Returns a data frame containing vectors as columns."""
def Vectorize(*texts):
    tfidf = vectorizer.fit_transform(texts)
    return tfidf

if __name__ == '__main__':
    #BAG OF WORDS OBJECTS
    trump_BOW = ""
    bernie_BOW = ""
    trump_tweets_BOW = ""
    bernie_tweets_BOW = ""
    trumpf_tweets_BOW = ""
    bernief_tweets_BOW = ""
    #Adding strings to a list

    #READING IN PRESS RELEASE FILE
    with open("../data/press_releases.json", 'rb') as f:
        for line in f:
            press_release = json.loads(line)
            author = press_release['author']
            text = press_release['text']
            if author == "Trump":
                trump_BOW += text
            else:
                bernie_BOW += text

    #READING IN TWEET FILE
    with open("../data/tweets3.json", 'rb') as f:
        for line in f:
            tweet = json.loads(line)
            #list_tweets.append(j)
            if tweet['luminary_followed'] == None:
            #Tweet is bernie or trump
                if tweet['user']['screen_name'] == "BernieSanders":
                    #tweet is by Bernie
                    bernie_tweets_BOW += " " + tweet['text']
                else:
                    #Tweet is by trume
                    trump_tweets_BOW += " " + tweet['text']
            #Tweet belongs to a follower
            elif tweet['luminary_followed'] == "realDonaldTrump":
                trumpf_tweets_BOW += " " + tweet['text']
                #Tweet is by trump follower
            elif tweet['luminary_followed'] == "BernieSanders":
                #Tweet is by bernie follower
                bernief_tweets_BOW += " " + tweet['text']

    print len(bernie_tweets_BOW), "Bernie tweets"
    print len(trump_tweets_BOW), "Trump tweets"
    print len(bernief_tweets_BOW), "Bernie follower tweets"
    print len(trumpf_tweets_BOW), "Trump follower tweets"

    texts = [trump_BOW,bernie_BOW,trump_tweets_BOW,
             bernie_tweets_BOW,trumpf_tweets_BOW,
             bernief_tweets_BOW]

    print "preprocessing"
    #PREPROCESSING EACH BoW
    texts = [Preprocess(x) for x in texts]

    print "vectorizing"
    ###COMPUTING TFIDF VECTORS
    vectors = Vectorize(*texts)

    ##COMPUTING COSINE SIMILARITY SCORES
    print "Comparing Trump and Bernie PR"
    print ((vectors * vectors.T))[0,1]

    print "Comparing Trump and Bernie Tweets"
    print ((vectors * vectors.T))[2,3]

    print "Comparing Trump PR and tweets"
    print ((vectors * vectors.T))[0,2]

    print "Comparing Bernie PR and tweets"
    print ((vectors * vectors.T))[1,3]

    print "Comparing Trump and Bernie Followers' Tweets"
    print ((vectors * vectors.T))[4,5]

    print "Comparing Trump tweets and his followers' Tweets"
    print ((vectors * vectors.T))[2,4]

    print "Comparing Bernie tweets and his followers' Tweets"
    print ((vectors * vectors.T))[3,5]