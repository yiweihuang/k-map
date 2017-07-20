import json
import sys
import os
import re
import ast
from itertools import groupby
from collections import OrderedDict

if len(sys.argv) < 3:
    print('Usage: python3 [].py cid chid')
    sys.exit()
else:
    cid = sys.argv[1]
    chid = sys.argv[2]

# get the next and previous key:value of a particular key in a dictionary
def iterate(iterable):
    iterator = iter(iterable)
    item = next(iterator)
    for next_item in iterator:
        yield item, next_item
        item = next_item
    yield item, None

def slice_page(path):
    same_page_arr = []
    outline_arr = []
    with open(path, 'r') as fr:
        str_content = []
        json_txt = json.load(fr)
        end_page = len(json_txt) + 1
        for page in json_txt:
            json_txt[page].pop(str(len(json_txt[page])))
            str_content.append(str(json_txt[page]))
        dups = [x for x in str_content if str_content.count(x) > 1]
        for line in list(set(dups)):
            temp_ = []
            for outline in range(2, len(ast.literal_eval(line)) +1):
                word = ast.literal_eval(line)[str(outline)]['Content']
                word = word.strip()
                temp_.append(word)
            same_page_arr.append([i+1 for i, x in enumerate(str_content) if x == line])
    index = list(len(l) for l in same_page_arr).index(max(list(len(l) for l in same_page_arr)))
    same_page_arr[index].append(end_page)
    return same_page_arr

def slice_tree(page_arr):
    for page in page_arr:
        for item, next_item in iterate(page):
            if next_item != None:
                print(item)
                print(next_item)

if __name__ == '__main__':
    slide_path = 'slide_layer/' + cid + '/' + chid + '.json'
    same_page_arr = slice_page(slide_path)
    # if len(same_page_arr) != 0:
        # slice_tree(same_page_arr)
