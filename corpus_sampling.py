# -*- coding: utf-8 -*-
import pickle
import os
from nltk import RegexpTokenizer
from nltk.data import load
import argparse


LANG = 'rus'
CORPUS_LOCATION = "/Volumes/Seagate/language data/ru_wikipedia/articles/wiki_sent_tok_id"
CONFUSION_SET_LOCATION = "filtered_popular_pairs_include_prepositions.txt"
DUMP_LOCATION = "some path"


parser = argparse.ArgumentParser(description='Create ')
parser.add_argument('CORPUS_LOCATION', type=str,
                    help='file with list of files')
parser.add_argument('CONFUSION_SET_LOCATION', type=str,
                    help='depending on the mode stream/file reads and output words from stream or from the same file as dictionary')
parser.add_argument('DUMP_LOCATION', type=str,
                    help='file with list of files')
parser.add_argument('-l', dest='LANG', type=str,
                    help='destination to write word pairs in the mode \'file\'')


class SentenceTokenizer:
    def __init__(self, lang="rus"):
        if lang == 'rus':
            language = 'russian'
        elif lang == 'eng':
            language = 'english'
        else:
            raise NotImplementedError()

        self.tokenizer = load("tokenizers/punkt/{0}.pickle".format(language))

    def tokenize(self, text):
        return self.tokenizer.tokenize(text)


def create_tokenizer():
    tokenizer = RegexpTokenizer("[A-Za-zА-Яа-я-]+|[^\w\s]")
    
    return lambda sentence: tokenizer.tokenize(sentence)


def create_sentencizer():
    sent_tokenizer = SentenceTokenizer(LANG)

    return lambda line: sent_tokenizer.tokenize(line)


def load_confusion_set(confusion_set_location):
    """
    Return a set of all words that appear in the confusion set
    """
    def load_pair_list():
        pairs = open(confusion_set_location, "r").read().split("\n")
        pairs = map(lambda x: tuple(x.split("; ")[:2]), pairs)
        return pairs

    target_words = set()
    pairs = load_pair_list()
    for pair in pairs:
        for word in pair:
            target_words.add(word)

    return pairs, target_words


def corpus_reader(corpus_location):
    sentencize = create_sentencizer()

    for line in open(corpus_location, "r"):
        sentences = sentencize(line)
        for sentence in sentences:
            yield sentence


def create_word_sentence_map(corpus_location, target_words):
    tokenize = create_tokenizer()
    word_sentence_map = dict()

    for sent_ind, sentence in enumerate(corpus_reader(corpus_location)):
        for token in tokenize(sentence):

            if token in target_words:
                if sent_ind in word_sentence_map:
                    word_sentence_map[token].add(sent_ind)
                else:
                    word_sentence_map[token] = set()
                    word_sentence_map[token].add(sent_ind)

    return word_sentence_map


def get_sentences_for_pairs(pairs, word2sentence):
    sentence_pair_map = dict()

    for pair in pairs:
        word1, word2 = pair
        candidates = word2sentence[word1] | word2sentence[word2]

        # filter by number of availeble sentences for a pair
        candidates = subsample(candidates)

        for candidate in candidates:
            if candidate in sentence_pair_map:
                sentence_pair_map[candidate].add(pair)
            else:
                sentence_pair_map[candidate] = set()
                sentence_pair_map[candidate].add(pair)

    return sentence_pair_map


def dump_sentences(sentence2pair, corpus_location, dump_location):

    def dump_sentence(location, pair, sentence):
        # assumes pair words are sorted 
        path = os.path.join(location, "%s_%s.txt" % pair)
        with open(path, "a") as pair_file:
            pair_file.write(sentence+"\n")

    for sent_ind, sentence in enumerate(corpus_reader(corpus_location)):
        if sent_ind in sentence2pair:
            for pair in sentence2pair[sent_ind]:
                dump_sentence(dump_location, pair, sentence)


pairs, target_words = load_confusion_set(CONFUSION_SET_LOCATION)

word2sentence = create_word_sentence_map(CORPUS_LOCATION, target_words)

sentence2pair = get_sentences_for_pairs(pairs, word2sentence)

dump_sentences(sentence2pair, CORPUS_LOCATION, DUMP_LOCATION)