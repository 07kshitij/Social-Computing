import os
import csv
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import mutual_info_classif, SelectKBest
from sklearn.model_selection import cross_validate
from sklearn.svm import SVC
from string import punctuation
from copy import deepcopy
from sklearn.naive_bayes import MultinomialNB


TRAIN_PATH = os.path.join("..", os.path.join("data", "train.tsv"))
TEST_PATH = os.path.join("..", os.path.join("data", "test.tsv"))
RESULT_PATH = os.path.join("..", 'predictions')

# Lists which are populated with the test / train tweets and labels

train_tweets = []
test_tweets = []
train_labels = []
test_labels = []
train_id = []
test_id = []

DEBUG = False


def preprocess(data):
    """
        Removes punctuations from the tweets
    """
    for token in punctuation:
        data = data.replace(token, " ")
    data = data.replace("  ", " ").lower().strip()
    return data


def get_cross_validation_score(clf, train_vectors, train_labels, cv=3, scoring='f1_macro'):
    """
        3 Fold Cross validation with macro f1 score as metric
        Used to observe accuracy of classifier when training
    """
    cv_results = cross_validate(clf, train_vectors, train_labels, cv=cv, scoring='f1_macro')
    return (sum(cv_results['test_score']) / len(cv_results['test_score']))


def load_data(data_path):
    """
        Loads the .tsv file pointed out by 'data_path'
        Returns the id, tweets and labels (if any) in the file
    """
    data_file = open(data_path, "r", encoding="utf-8")
    data = csv.reader(data_file, delimiter="\t", quotechar=None)
    header = True
    ids = []
    tweets = []
    labels = []
    for line in data:
        if not header:
            ids.append(line[0])
            tweets.append(preprocess(line[1]))
            try:
                labels.append(int(line[2]))
            except IndexError:
                pass
        header = False
    return ids, tweets, labels


def write_results(file_name, test_labels):
    """
        Writes the predicted 'test_labels' to the output file 'file_name'
    """
    outFile = open(os.path.join(RESULT_PATH, file_name), "w", encoding='utf-8')
    writer = csv.DictWriter(outFile, fieldnames=["id", "hateful"])
    writer.writeheader()

    for pos in range(len(test_labels)):
        writer.writerow(
            {
                "id": test_id[pos],
                "hateful": test_labels[pos]
            }
        )
    outFile.close()


def multinomialNB(train_tweets, test_tweets):

    """
        Runs the Multinomial Naive Bayes Classifier with Feature Selection
        Feature Selection is based on Mutual Information scores
    """

    if DEBUG:
        print('Running Multinomial Naive Bayes Classifier')

    vectorizer = CountVectorizer(min_df=5, max_df=0.9)

    train_vectors = vectorizer.fit_transform(train_tweets)
    test_vectors = vectorizer.transform(test_tweets)

    # Select the top 2000 features based on Mutual Information score
    topK = SelectKBest(mutual_info_classif, k=2000)
    train_vectors = topK.fit_transform(train_vectors, train_labels)
    test_vectors = topK.transform(test_vectors)

    randomForestClf = MultinomialNB()
    if DEBUG:
        print(get_cross_validation_score(
            randomForestClf, train_vectors, train_labels))
    randomForestClf.fit(train_vectors, np.array(train_labels))
    test_labels = randomForestClf.predict(test_vectors)

    write_results("T2.csv", test_labels)


if __name__ == "__main__":

    if not os.path.exists(RESULT_PATH):
        os.makedirs(RESULT_PATH)

    train_id, train_tweets, train_labels = load_data(TRAIN_PATH)
    test_id, test_tweets, test_labels = load_data(TEST_PATH)

    multinomialNB(train_tweets, test_tweets)
