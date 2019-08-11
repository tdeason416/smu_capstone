#/usr/bin/python
import pandas as pd;
import numpy as np;
import os
import requests
import bs4 as bs
import nltk
import re
import time
import sys
import json
from collections import Counter
import logging
import multiprocessing;
#from wordcloud import WordCloud, ImageColorGenerator
#from itertools import cycle

from nltk.corpus import words, stopwords
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize, sent_tokenize, pos_tag
#from gensim import corpora
import spacy
#spacy.load('en')
from spacy.lang.en import English


#################
## Arguements
#################

more_stop_words = ['company','months','products','operations','income','period','sales','market','business','stock','results',
                  'revenue','shares','share','revenues','assets','statements','value','costs','product','quarter','increase',
                  'expense','customers','performance','interest','charges','price','compensation','agreement','property','amount',
                  'markets','information','expenses','facility','customer','taxes','demand','payments',
                  'stringitemtype','textblockitemtype']

en_stop = nltk.corpus.stopwords.words('english')
en_stop.extend(more_stop_words)
parser = English()

#################
## SOME FUNCTIONS
#################

def load_filings(folder_name):
    filings = []
    files = os.listdir(folder_name)
    for file in files:
        filing = open(folder_name + '/' + file).read()
        filings.append(filing)
    return filings

def get_text_from_file(fl):
    page_soup = bs.BeautifulSoup(open(fl), 'lxml')
    divs = page_soup.find_all('div')
    all_text = []
    for div in divs:
        text = div.getText()
        if len(text) > 200 and text[0] != '\xa0':
            all_text.append(text)
    return "\n".join(all_text)

def combine_text(text):
    file = ""
    for i in range(len(text)):
        ## removes all the /xa0 /n /t garbage and some extra spaces
        cleaner_text = re.sub('\s+', ' ', text[i]).strip()
        fh = fh + " " + cleaner_text
    return fh

def get_all_files(files):
    all_files = []
    for file in files:
        text = get_text_from_file(file)
        #filing = combine_text(text)
        all_files.append(filing)
    return all_files

def tokenize(text):
    '''
    Separates each word from the others, making them lower case and removing URLs and possible screen names that show up.
    '''
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

def combine_lists(list_of_lists):
    out = [] 
    for li in list_of_lists:
        out += li
    return out 

def prepare_text(fh):
    '''
    Tokenizes the text, removes short words, removes stop words, and then gets the lemma of each word.
    '''
    try:
        text = get_text_from_file(fh)
        #open(fh).read()
    except UnicodeDecodeError:
        return None
    if len(text)> 10**6 - 1 :
        inc = 10**6 - 1
        tokens = []
        i = 0
        while i < len(text):
            tokens += tokenize(text[i:i + inc])
            i += inc
        #texts = [tokenize(text[(i-1) * inc : i * inc]) for i in range(0, len(text), 10**6)]
        #tokens = combine_lists(texts)
    else:
        tokens = tokenize(text)
    new_tokens = []
    for tok in tokens:
        if len(tok) > 4 and tok[0] not in {'-', 'x'} and tok not in en_stop:
            new_tokens.append(tok)
    pos_tags = nltk.pos_tag(new_tokens)
    #print(pos_tags[:3])
    token_counts = Counter()
    for tag in pos_tags:
        if tag[1][0] == 'N':
            token_counts[tag[0]] += 1
    #pos_tokens = [pos_tag[0] for pos_tag in pos_tags if pos_tag[1][0] == "N"]
    #final_text = ""
    return json.dumps(token_counts)


#################
## Main Function
#################

def main(input_folder, output_folder):
    '''
    NOTE the last character for input_folder/output_folder must be a "/" for this function to work
    '''
    in_files = os.listdir(input_folder)
    out_files = set(os.listdir(output_folder))
    for f in in_files:
        if f not in out_files:
            #prepare_text(input_folder + f)
            prepared = prepare_text(input_folder + f)
            if prepared:
                open(output_folder + f, 'w').write(prepare_text(input_folder + f))
                print(f, " completed")

if __name__ == "__main__":
    in_folder = input("location of raw html (must include '/')")
    out_folder = input("location to save .json files (must include '/')")
    main(in_folder, out_folder)
