import nltk
import sys
import os
import math

from nltk import word_tokenize

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    contents = {}
    for file in os.listdir(f'{directory}/'):
        pathname = directory + '/' + file
        # split and re-join path to ensure the function works cross- platform
        os.path.split(pathname)
        os.path.join(pathname)

        with open(f'{pathname}', 'r') as f:
            fileRead = f.read()
            contents[file] = fileRead

    return contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    # list of words with punctuation removed (periods remaining)
    tokenized = word_tokenize(document)
    stopwords = nltk.corpus.stopwords.words("english")

    # cleaned up list of words to ultimately return i.e. all lowercase with punctuaton and stopwords filtered out
    documentWords = [word.lower() for word in tokenized if word.isalpha() and word not in stopwords]

    return documentWords

def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    totalDocuments = len(documents)

    # dictionary to store for each word the number of documents in which this word appears
    wordFrequencies = {}

    for document in documents:
        wordsInThisDoc = []
        for word in documents[document]:
            if word not in wordsInThisDoc and word in wordFrequencies:
                wordFrequencies[word] += 1
                wordsInThisDoc.append(word)
            elif word not in wordsInThisDoc:
                wordFrequencies[word] = 1
                wordsInThisDoc.append(word)

    # for each word, calculate its IDF i.e. log of totalDocuments over the number of docs in which each word appear
    IDFs = {}
    for word in wordFrequencies:
        IDFs[word] = math.log(totalDocuments/wordFrequencies[word])

    return IDFs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    topFiles = []

    # dict to keep track of the overall score for each file i.e. the sum of each file's tf-idf values for words that appear in the query and the file
    fileScores = {}

    for file in files:
        # store term frequencies for each individual word that appears in both the query and the file
        termFrequencies = dict((word, files[file].count(word)) for word in query if word in files[file])

        # calculate the tf-idf values for each word in the file
        tf_idf = {}

        for word in termFrequencies:
            tf_idf[word] = termFrequencies[word] * idfs[word]

        fileScores[file] = sum(tf_idf.values())

    # order the files in fileScores by the scores of each file
    sortedFileScores = sorted(fileScores, key = fileScores.get, reverse = True)

    # return the n most relevant filenames
    return sortedFileScores[0:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    sentenceScores = []

    for sentence in sentences:

        # tuple to hold the matchingWordMeasure and queryTermDensity for a sentence
        sentenceProperties = [sentence]

        # calculate sum of idf values for words in the sentence which also appear in the query
        matchingWordMeasure = sum([idfs[word] for word in query if word in sentences[sentence]])

        sentenceProperties.append(matchingWordMeasure)

        # this is the proportion of words in the sentence that are also words in the query

        queryTermDensity = len([word for word in query if word in sentence])/len(sentence)

        sentenceProperties.append(queryTermDensity)

        sentenceScores.append(sentenceProperties)

    # order the sentenceScores in decreasing order if sentence scores (including tie breaking based on queryTermDensity)
    #sortedSentenceScores = sorted((sorted(sentenceScores, key = lambda x: x[0], reverse=True)), key = lambda x: x[1])


    sortedSentenceScores = sorted(sentenceScores, key = lambda key: (key[1], key[2]), reverse=True)

    for i in range(len(sortedSentenceScores)):
        print(f"{i}: {sortedSentenceScores[i]}")
    # this sorts just based on matchingWordMeasure
    #sortedSentenceScores = sorted(sentenceScores, key = sentenceScores.get, reverse = True)
    # return the n sentences with the highest scores
    return sortedSentenceScores[0:n]


if __name__ == "__main__":
    main()
