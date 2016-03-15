"""
Use NLTK + SciKit learn to classify tweets as "Bernie" or "Trump"
    Bernie = 1
    Trump = 0

We can use a range of models:
    SVM
    Naive Bayes
    Logistic Regression
    Lasso
    Decision Tree
    Decision Forest
    GBDT

This script has two parts:
    1) Feature Creation
    2) Model Fitting

Part #1 is more important for NLP work

We use AUC curves to evaluate model performance
These easily display the precision/recall at various classificastion thresolds

F2 measures are also useful
"""
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn import cross_validation
from sklearn import naive_bayes
import nltk
from nltk.tokenize import TweetTokenizer
import pandas as pd
from textstat.textstat import textstat
from ggplot import *

tweet_tokenizer = TweetTokenizer(reduce_len=True)

stemmer = nltk.stem.porter.PorterStemmer()
stopwords = nltk.corpus.stopwords.words("english")
other_exclusions = ["ff", "rt"]
stopwords.extend(other_exclusions)

## Feature Creation ##

### Feature Creation Functions ###

def preprocess(text_string):
    """
    Accepts a text string and replaces:
    1) urls with URLHERE
    2) lots of whitespace with one instance
    3) mentions with MENTIONHERE

    This allows us to get standardized counts of urls and mentions
    Without caring about specific people mentioned
    """
    space_pattern = '\s+'
    giant_url_regex = ('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
        '[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    mention_regex = '@[\w\-]+'
    parsed_text = text_string.lower()
    parsed_text = re.sub(space_pattern, ' ', text_string)
    parsed_text = re.sub(giant_url_regex, 'URLHERE', parsed_text)
    parsed_text = re.sub(mention_regex, 'MENTIONHERE', parsed_text)
    return parsed_text

def tokenizer(text_string):
    """
    A soup-to-nuts tokenizer
    Does all of the processing we want
    """
    preprocessed_text = preprocess(text_string)
    tokens = nltk.word_tokenize(preprocessed_text)
    return tokens

def stemming_tokenizer(text_string):
    """
    Exactly like the tokenizer function but with stemmer
    """
    preprocessed_text = preprocess(text_string)
    tokens = tweet_tokenizer(preprocessed_text)
    stems = [stemmer.stem(t) for t in tokens]
    return stems

def extra_features(text_string):
    """
    Sometimes we want to hand craft features, this does that
    Should create that preprocess + tokenizer can't
    Takes a text string, returns counts of features
    """
    flesch = textstat.flesch_reading_ease(tweet)
    flesch_kincaid = textstat.flesch_kincaid_grade(tweet)
    gunning_fog = textstat.gunning_fog(tweet)
    return flesch, flesch_kincaid, gunning_fog

if __name__ == '__main__':
    vectorizer = TfidfVectorizer(
        tokenizer=tokenizer,
        ngram_range=(1, 2),
        stop_words=stopwords,
    )
    list_of_dicts = []
    with open('../data/tweet_text.json', 'rb') as f:
        for line in f:
            j = json.loads(line)
            author_status = j['author_status']
            if author_status == 'Trump':
                j['author_status'] = 0
                list_of_dicts.append(j)
            elif author_status == 'Bernie':
                j['author_status'] = 1
                list_of_dicts.append(j)
            elif author_status == 'Trump follower':
                j['author_status'] = 2
                list_of_dicts.append(j)
            elif author_status == 'Bernie follower':
                j['author_status'] = 3
                list_of_dicts.append(j)
            else:
                # keep only bernie/trump tweets for now
                continue

    # Use scipy data frame because it plays nice with numpy/scipy
    # Also handles strings nicely
    df = pd.DataFrame(list_of_dicts)
    # This is the syntax to pull out columns of the df

    # Trump v Bernie
    # Select rows that correspond to Bernie or Trump tweets only
    trump_bernie_df = df[df['author_status'] < 2].copy()

    y = trump_bernie_df['author_status']
    X = trump_bernie_df['text']
    vectorizer.fit(X)
    X = vectorizer.transform(X)

    X_train, X_test, y_train, y_test = cross_validation.train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    bnb = naive_bayes.BernoulliNB()
    bnb.fit(X_train, y_train)
    y_pred = bnb.predict(X_test)
    print(len(y_pred))
    print(sum(abs(y_pred - y_test)))

    # AUC-ROC
    # area under receiver operator curve
    y_pred = bnb.predict_proba(X_test)[:,1]
    fpr, tpr, _ = metrics.roc_curve(y_test, y_pred)

    roc_df = pd.DataFrame(dict(fpr=fpr, tpr=tpr))
    #g = ggplot(roc_df, aes(x='fpr',y='tpr')) +\
    #    geom_line() +\
    #    geom_abline(linetype='dashed')
    # print(g)

    # Follower classification
    follower_df = df[df['author_status'] > 1].copy()
    # follower_df = follower_df.iloc[0:100,:]
    follower_df['author_status'] -= 2

    print(follower_df)

    y_follower = follower_df['author_status']
    print('made y')
    X_follower = vectorizer.transform(follower_df['text'])
    print('made x')
    print(y_follower)
    y_follower_pred_prob = bnb.predict_proba(X_follower)[:,1]
    y_follower_pred = bnb.predict(X_follower)
    # summary measures here

    print(metrics.f1_score(y_follower, y_follower_pred))

    fpr, tpr, _ = metrics.roc_curve(y_follower, y_follower_pred_prob)
    roc_df = pd.DataFrame(dict(fpr=fpr, tpr=tpr))
    print(roc_df)
    g = ggplot(roc_df, aes(x='fpr',y='tpr')) +\
        geom_line() +\
        geom_abline(linetype='dashed')
    print(g)

    # retrain this on followers #
