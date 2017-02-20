import json
import sys
import os
import re
import itertools
from collections import OrderedDict

if len(sys.argv) < 3:
    print('Usage: python3 [].py type week1')
    sys.exit()
else:
    type_ = sys.argv[1]
    week_num = sys.argv[2]

# using the file of the tfidf to get the normal distribution
def get_keyword(path):
    tfidf_keyword = []
    with open(path, 'r') as fr:
        for line in fr:
            word = re.sub(r'[\u4e00-\u9fff]+', '', line.split('\t')[0])
            word = word.strip()
            tfidf_keyword.append(word)
    return tfidf_keyword

# check if a sentence contains a certain word
def fit_word(doc, tfidf_keyword):
    fit_word_arr = []
    word = re.sub(r'[\u4e00-\u9fff]+', '', doc)
    word = re.sub(r'[().,…:@=?+]+', ' ', word)
    for keyword in tfidf_keyword:
        if word.lower().find(keyword.lower()) > 0:
            fit_word_arr.append(keyword)
    # word_arr = word.split(' ')
    # fit_word_arr = []
    # for content in word_arr:
    #     if(re.match(r'[A-Za-z]+', content) != None):
    #         if(len(content) > 1 and content[0].isupper() and content[1].islower()):
    #             content = content.lower()
    #         content = wnl.lemmatize(content)
    #         fit_word_arr.append(content)
    # fit_word_arr = [x for x in fit_word_arr if x not in cachedStopWords]
    # fit_word_arr = [y for y in fit_word_arr if len(y) != 1]
    # fit_word_arr = [x for x in fit_word_arr if x in tfidf_keyword]
    return fit_word_arr

#  find words of n-layer (n is 2,3,4)
def fix_layer(title, tfidf_keyword, json_txt, layer_num):
    temp_ = {}
    for page in json_txt:
        if title == json_txt[page]['1']['Content'].split('\n')[0]:
            for row, info in json_txt[page].items():
                if info['Layer'] == layer_num:
                    raw_sent = info['Content']
                    fit_word_arr = fit_word(raw_sent, tfidf_keyword)
                    if fit_word_arr:
                        fit_word_arr = list(set(fit_word_arr))
                        if len(fit_word_arr) > 1:
                            word_string = ','.join(fit_word_arr)
                            temp_[int(row)] = word_string
                        else:
                            temp_[int(row)] = fit_word_arr[0]
    return temp_

#  find words of more than n-layer (n is 5)
def until_layer(title, tfidf_keyword, json_txt, layer_num):
    temp_ = {}
    for page in json_txt:
        if title == json_txt[page]['1']['Content'].split('\n')[0]:
            for row, info in json_txt[page].items():
                if info['Layer'] >= layer_num:
                    raw_sent = info['Content']
                    fit_word_arr = fit_word(raw_sent, tfidf_keyword)
                    if fit_word_arr:
                        fit_word_arr = list(set(fit_word_arr))
                        if len(fit_word_arr) > 1:
                            word_string = ','.join(fit_word_arr)
                            temp_[int(row)] = word_string
                        else:
                            temp_[int(row)] = fit_word_arr[0]
    return temp_

# get the next and previous key:value of a particular key in a dictionary
def iterate(iterable):
    iterator = iter(iterable)
    item = next(iterator)
    for next_item in iterator:
        yield item, next_item
        item = next_item
    yield item, None

# title - layer_1
def build_layer_first(title, layer_first):
    all_ = ()
    layer_first = OrderedDict(sorted(layer_first.items()))
    for first_key in layer_first:
        tup = ((title, layer_first[first_key]),)
        all_ = all_ + tup
    return all_

# layer_n - layer_n+1 (n is 1,2,3,4)
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

def paser_step_one(path):
    title = []
    with open(path, 'r') as fr:
        json_txt = json.load(fr)
        for page in json_txt:
            if page != '1':
                title_name = json_txt[page]['1']['Content']
                title_name = title_name.split('\n')[0]
                if title_name not in title:
                    title.append(title_name)
    return title

def paser_step_two(type_, week_num, path, layer_one):
    if type_ == '1':
        tfidf_keyword = get_keyword('keyword-extra/slide/' + week_num + '.txt')
    elif type_ == '2':
        tfidf_keyword = get_keyword('keyword-extra/slide_add_book/' + week_num + '.txt')
    with open(path, 'r') as fr:
        json_txt = json.load(fr)
        done_ = ()
        for one in layer_one:
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
                print(tup)
                second_ = second_ + tup
            done_ = done_ + first_ + second_
        return done_

def tup_dict_to_tree(type_, name, links):
    name_to_node = {}
    root = {'name': name, 'children': []}
    for parent, child in links:
        parent_node = name_to_node.get(parent)
        if not parent_node:
            name_to_node[parent] = parent_node = {'name': parent}
            root['children'].append(parent_node)
        name_to_node[child] = child_node = {'name': child}
        parent_node.setdefault('children', []).append(child_node)
    if type_ == '1':
        os.remove('map-tree/slide/' + name + '.json') if os.path.exists('map-tree/slide/' + name + '.json') else None
        with open('map-tree/slide/' + name + '.json', 'w') as outfile:
            json.dump(root, outfile, indent=4)
    elif type_ == '2':
        os.remove('map-tree/slide_add_book/' + name + '.json') if os.path.exists('map-tree/slide_add_book/' + name + '.json') else None
        with open('map-tree/slide_add_book/' + name + '.json', 'w') as outfile:
            json.dump(root, outfile, indent=4)

if __name__ == '__main__':
    data = 'slide_layer/' + week_num + '.json'
    layer_one = paser_step_one(data)
    tup_dict = paser_step_two(type_, week_num, data, layer_one)
    tup_dict_to_tree(type_, week_num, tup_dict)
