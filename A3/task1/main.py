import os
import csv
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_validate
from sklearn.svm import SVC
from string import punctuation
from copy import deepcopy
import spacy
import fasttext

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
all_tweets = []

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
                labels.append(line[2])
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


def RandomForest():

    """
        Runs the RandomForest Classifier with tf_idf embedding
    """

    if DEBUG:
        print('Running Random Forest')

    vectorizer = TfidfVectorizer(min_df=5, max_df=0.8)
    # Obtain the sparse matrix containing the tf-idf vectors
    tf_idf_vectors = vectorizer.fit_transform(all_tweets)

    train_vectors = tf_idf_vectors[:len(train_tweets)]
    test_vectors = tf_idf_vectors[len(train_tweets):]

    randomForestClf = RandomForestClassifier(random_state=0)
    if DEBUG:
        print(get_cross_validation_score(randomForestClf, train_vectors, train_labels))
    randomForestClf.fit(train_vectors, np.array(train_labels))
    test_labels = randomForestClf.predict(test_vectors)

    write_results("RF.csv", test_labels)


def SVMClassifier():

    """
        Runs the SVM Classifier with Word2Vec Embeddings
    """

    if DEBUG:
        print('Running SVM')

    # Spacy English Language model
    langModel = spacy.load('en_core_web_md')

    corpus = []
    counter = 0
    for tweet in all_tweets:
        tokens = langModel(tweet)
        embeddings = tokens.vector
        corpus.append(embeddings)
        counter += 1
        if DEBUG and counter % 100 == 0:
            print('Embeddings calculated for {} tweets'.format(counter))

    train_vectors = corpus[:len(train_tweets)]
    test_vectors = corpus[len(train_tweets):]

    SVMclf = SVC(random_state=0)
    if DEBUG:
        print(get_cross_validation_score(SVMclf, train_vectors, train_labels))
    SVMclf.fit(train_vectors, np.array(train_labels))
    test_labels = SVMclf.predict(test_vectors)

    write_results("SVM.csv", test_labels)


def prepare_train_file():

    """
        Generates the train file required by 'FastText' containing labels prefixed with __label__
    """

    outFile = open('data.train.txt', 'w', encoding='utf-8')
    for idx in range(len(train_tweets)):
        outFile.write('__label__{} {}\n'.format(
            train_labels[idx], train_tweets[idx]))
    outFile.close()


def FastText():

    """
        Runs the Supervised FastText classifier
    """

    if DEBUG:
        print('Running Fasttext')

    # Generate the specific train file required by fasttext
    prepare_train_file()

    model = fasttext.train_supervised('data.train.txt')
    results = model.predict(test_tweets)

    for idx in range(len(test_tweets)):
        label = results[0][idx][0]
        if label == '__label__0':
            label = '0'
        else:
            label = '1'
        test_labels.append(label)

    write_results("FT.csv", test_labels)


if __name__ == "__main__":

    if not os.path.exists(RESULT_PATH):
        os.makedirs(RESULT_PATH)

    # Read test / train tweets to lists
    train_id, train_tweets, train_labels = load_data(TRAIN_PATH)
    test_id, test_tweets, test_labels = load_data(TEST_PATH)

    all_tweets = deepcopy(train_tweets)
    all_tweets.extend(test_tweets)

    RandomForest()
    SVMClassifier()
    FastText()
