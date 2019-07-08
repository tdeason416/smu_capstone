import pandas as pd;
import numpy as np;
import os
import requests
import bs4 as bs
import nltk
import re
import time
import sys
import logging
import multiprocessing;
#from wordcloud import WordCloud, ImageColorGenerator
#from itertools import cycle

#################
## Arguements
#################


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

def get_text_from_file(file):
    page_soup = bs.BeautifulSoup(file, 'lxml')
    divs = page_soup.find_all('div')
    all_text = []
    for div in divs:
        text = div.getText()
        if len(text) > 200 and text[0] != '\xa0':
            all_text.append(text)
    return all_text

def combine_text(text):
    file = ""
    for i in range(len(text)):
        ## removes all the /xa0 /n /t garbage and some extra spaces
        cleaner_text = re.sub('\s+', ' ', text[i]).strip()
        file = file + " " + cleaner_text
    return file

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
        out.append(li)
    return out

def prepare_text(text):
    '''
    Tokenizes the text, removes short words, removes stop words, and then gets the lemma of each word.
    '''
    #if len(text)> 2*(10**6)-1 :
    #    print(len(text))
    
    if len(text)> 10**6 - 1 :
        inc = 10**6
        texts = [text[(i-1) * inc : i * inc]
        #text1 = text[:999999]
        #text2 = text[999999:]
        #tokens = tokenize(text1) + tokenize(text2)
        tokens = combine_lists(texts)
    else:
        tokens = tokenize(text)
        
    #tokens = [token for token in tokens if len(token) > 4]
    #tokens = [token for token in tokens if token[0]!='-']
    #tokens = [token for token in tokens if token[0]!='x']
    #tokens = [token for token in tokens if token not in en_stop]
   
    new_tokens = []
    for tok in tokens:
        if len > 4 and tok[0] not in {'-', 'x'} and tok not in en_stop:
            new_tokens.append(tok)
    pos_tags = nltk.pos_tag(new_tokens)
    pos_tokens = [pos_tag[0] for pos_tag in pos_tags if pos_tag[1][0] == "N"]
    #final_text = ""
    return pos_tokens

def prepare_all(all_files):
    prepared_filings = []
    for file in all_files:
        tokens = prepare_text(file)
        prepared_filings.append(tokens)
    
    return prepared_filings 
