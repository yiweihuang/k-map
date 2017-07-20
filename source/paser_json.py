import json
import os
import re
import itertools
import numpy as np
from collections import OrderedDict
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

wnl = WordNetLemmatizer()
cachedStopWords = stopwords.words("english")

# using the file of the tfidf to get the normal distribution
def create_normal(path):
    normal_arr = []
    temp_dict = {}
    tfidf_keyword = []
    with open(path, 'r') as fr:
        for line in fr:
            normal_arr.append(float(line.split('\t')[1].split('\n')[0]))
            word = re.sub(r'[\u4e00-\u9fff]+', '', line.split('\t')[0])
            temp_dict[word] = float(line.split('\t')[1].split('\n')[0])
    mu = np.average(normal_arr)
    final_mu = round(mu)
    fr.close()
    for k, v in temp_dict.items():
        if v > final_mu:
            k = k.split(' ')
            tfidf_keyword = tfidf_keyword + k
    return tfidf_keyword

#
def fit_word(doc, tfidf_keyword):
    word = re.sub(r'[\u4e00-\u9fff]+', '', doc)
    word = re.sub(r'[().,…:@=?+]+', ' ', word)
    word_arr = word.split(' ')
    fit_word_arr = []
    for content in word_arr:
        if(re.match(r'[A-Za-z]+', content) != None):
            if(len(content) > 1 and content[0].isupper() and content[1].islower()):
                content = content.lower()
            content = wnl.lemmatize(content)
            fit_word_arr.append(content)
    fit_word_arr = [x for x in fit_word_arr if x not in cachedStopWords]
    fit_word_arr = [y for y in fit_word_arr if len(y) != 1]
    fit_word_arr = [x for x in fit_word_arr if x in tfidf_keyword]
    return fit_word_arr

def fix_layer(title, tfidf_keyword, json_txt, layer_num):
    temp_ = {}
    for page in json_txt:
        if title == json_txt[page]['1']['Content'].split('\n')[0]:
            for row, info in json_txt[page].items():
                if info['Layer'] == layer_num:
                    raw_sent = info['Content']
                    fit_word_arr = fit_word(raw_sent, tfidf_keyword)
                    if fit_word_arr:
                        temp_[int(row)] = list(set(fit_word_arr))
    return temp_

def until_layer(title, tfidf_keyword, json_txt, layer_num):
    temp_ = {}
    for page in json_txt:
        if title == json_txt[page]['1']['Content'].split('\n')[0]:
            for row, info in json_txt[page].items():
                if info['Layer'] >= layer_num:
                    raw_sent = info['Content']
                    fit_word_arr = fit_word(raw_sent, tfidf_keyword)
                    if fit_word_arr:
                        temp_[int(row)] = fit_word_arr
    return temp_

def iterate(iterable):
    iterator = iter(iterable)
    item = next(iterator)
    for next_item in iterator:
        yield item, next_item
        item = next_item
    yield item, None

def build_layer_first(title, layer_first):
    all_ = ()
    layer_first = OrderedDict(sorted(layer_first.items()))
    for first_key in layer_first:
        tup = ((str([title]), str(layer_first[first_key])),)
        all_ = all_ + tup
    return all_


def build_layer(pre, next_):
    all_ = ()
    if next_ != None:
        pre = OrderedDict(sorted(pre[1].items()))
        next_ = OrderedDict(sorted(next_[1].items()))
        for next_key in next_:
            tup = ()
            for pre_key in pre:
                if next_key > pre_key:
                    tup = ((str(pre[pre_key]), str(next_[next_key])),)
            all_ = all_ + tup
    return all_

def create_tree(name, links):
    name_to_node = {}
    root = {'name': name, 'children': []}
    for parent, child in links:
        parent_node = name_to_node.get(parent)
        if not parent_node:
            name_to_node[parent] = parent_node = {'name': parent}
            root['children'].append(parent_node)
        name_to_node[child] = child_node = {'name': child}
        parent_node.setdefault('children', []).append(child_node)
    os.remove(name + '.json') if os.path.exists(name + '.json') else None
    with open(name + '.json', 'w') as outfile:
        json.dump(root, outfile, indent=4)
    return root

def paser_step_one(path):
    week_dict = {}
    for week in os.listdir(path):
        key = week.split('.')[0]
        with open(path + week, 'r') as fr:
            title = []
            json_txt = json.load(fr)
            for page in json_txt:
                if page != '1':
                    title_name = json_txt[page]['1']['Content']
                    title_name = title_name.split('\n')[0]
                    if title_name not in title:
                        title.append(title_name)
            week_dict[key] = title
    return week_dict

def paser_step_two(path, layer_one):
    tup_dict = {}
    for week in os.listdir(path):
        key = week.split('.')[0]
        tfidf_keyword = create_normal('dict/' + key + '.txt')
        with open(path + week, 'r') as fr:
            json_txt = json.load(fr)
            done_ = ()
            for one in layer_one[key]:
                layer_dict = {}
                layer_arr = []
                for page in json_txt:
                    if one == json_txt[page]['1']['Content'].split('\n')[0]:
                        for row, info in json_txt[page].items():
                            if info['Layer'] not in layer_arr:
                                layer_arr.append(info['Layer'])
                layer_arr = sorted(layer_arr)
                layer_arr.pop(0)
                for layer_i in layer_arr:
                    if layer_i < 5:  # layer
                        temp_ = fix_layer(one, tfidf_keyword, json_txt, layer_i)  # order - keyword
                        layer_dict[layer_i] = temp_
                until_temp = until_layer(one, tfidf_keyword, json_txt, 5)
                if until_temp:
                    layer_dict[5] = until_temp
                first_ = build_layer_first(one, layer_dict[2])
                second_ = ()
                for item, next_item in iterate(layer_dict.items()):
                    tup = build_layer(item, next_item)
                    second_ = second_ + tup
                done_ = done_ + first_ + second_
        tup_dict[key] = done_
    return tup_dict

def tup_dict_to_tree(tup_dict):
    for name in tup_dict:
        create_tree(name, tup_dict[name])

if __name__ == '__main__':
    data = 'slide_layer/'
    layer_one = paser_step_one(data)
    tup_dict = paser_step_two(data, layer_one)
    tup_dict_to_tree(tup_dict)
