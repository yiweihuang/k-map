#!/usr/bin/env python
import re
import os
from os import listdir
from os.path import isfile, join
import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter
import jieba
import re
from nltk.stem import WordNetLemmatizer
import math

if len(sys.argv) < 2:
    print('Usage: python3 [].py contents')
    sys.exit()
else:
    cid = sys.argv[1]

material_dir = '../k-map/slide/' + cid + '/'
pdf2txt_dir = '../k-map/slide_info/pdf2txt/' + cid + '/'
gramcount_dir = '../k-map/slide_info/gramcount/' + cid + '/'
tfidf_dir = '../k-map/slide_info/tfidf/' + cid + '/'
tfidf_com_dir = '../k-map/slide_info/tfidf_com/' + cid + '/'
result_dir = '../k-map/result/' + cid + '/'
files = [f for f in listdir(material_dir) if (isfile(join(material_dir, f)) and (re.match("[0-9A-Za-z&_]+.pdf",f) != None))]

# main
def pdf2txt(argv):
    import getopt
    def usage():
        print ('usage: %s [-d] [-p pagenos] [-m maxpages] [-P password] [-o output]'
               ' [-C] [-n] [-A] [-V] [-M char_margin] [-L line_margin] [-W word_margin]'
               ' [-F boxes_flow] [-Y layout_mode] [-O output_dir] [-R rotation]'
               ' [-t text|html|xml|tag] [-c codec] [-s scale]'
               ' file ...' % argv[0])
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dp:m:P:o:CnAVM:L:W:F:Y:O:R:t:c:s:')
    except getopt.GetoptError:
        return usage()
    if not args: return usage()
    # debug option
    debug = 0
    # input option
    password = ''
    pagenos = set()
    maxpages = 0
    # output option
    outfile = None
    outtype = None
    imagewriter = None
    rotation = 0
    layoutmode = 'normal'
    codec = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    laparams = LAParams()
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-p': pagenos.update( int(x)-1 for x in v.split(',') )
        elif k == '-m': maxpages = int(v)
        elif k == '-P': password = v
        elif k == '-o': outfile = v
        elif k == '-C': caching = False
        elif k == '-n': laparams = None
        elif k == '-A': laparams.all_texts = True
        elif k == '-V': laparams.detect_vertical = True
        elif k == '-M': laparams.char_margin = float(v)
        elif k == '-L': laparams.line_margin = float(v)
        elif k == '-W': laparams.word_margin = float(v)
        elif k == '-F': laparams.boxes_flow = float(v)
        elif k == '-Y': layoutmode = v
        elif k == '-O': imagewriter = ImageWriter(v)
        elif k == '-R': rotation = int(v)
        elif k == '-t': outtype = v
        elif k == '-c': codec = v
        elif k == '-s': scale = float(v)
    #
    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFResourceManager.debug = debug
    PDFPageInterpreter.debug = debug
    PDFDevice.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
        if outfile:
            if outfile.endswith('.htm') or outfile.endswith('.html'):
                outtype = 'html'
            elif outfile.endswith('.xml'):
                outtype = 'xml'
            elif outfile.endswith('.tag'):
                outtype = 'tag'
    if outfile:
        outfp = file(outfile, 'w')
    else:
        outfp = sys.stdout
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, codec=codec, laparams=laparams,
                              imagewriter=imagewriter)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, codec=codec, scale=scale,
                               layoutmode=layoutmode, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp, codec=codec)
    else:
        return usage()
    for fname in args:
        fp = file(fname, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.get_pages(fp, pagenos,
                                      maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            page.rotate = (page.rotate+rotation) % 360
            interpreter.process_page(page)
        fp.close()
    device.close()
    outfp.close()
    return

def txt2grams(intxt,outtxt):
    #jieba.set_dictionary('dict.txt.big')
    stop = open("../k-map/dict/stopwords.txt").read()
    lemmatizer = WordNetLemmatizer()
    max_ngram = 5
    ngram_counts = {}
    out = open(outtxt,"w")
    pattern = u'[A-Za-z/]+|[0-9]+\.[0-9]+|[\u4e00-\u9fa5]'
    with open(intxt) as text_file:
        for line in text_file:
            words_line = jieba.cut(line.strip(), cut_all=False)
            words_line = list(words_line)
            #words_line = re.findall(pattern,unicode(line,"utf-8"))

            #Data Clean
            words_line_clean = []
            for word in words_line:
                if(re.match(pattern,word)!=None and word.encode('utf-8') not in stop):
                    words_line_clean.append(word)

            for i in range(len(words_line_clean)):
                if(re.match(u"[A-Za-z]+",words_line_clean[i])!=None):
                    if(len(words_line_clean[i])>1 and words_line_clean[i][0].isupper() and words_line_clean[i][1].islower()):
                        words_line_clean[i] = words_line_clean[i].lower()
                    words_line_clean[i] = lemmatizer.lemmatize(words_line_clean[i])

            #Ngram Processing
            for i in range(len(words_line_clean)):
                for n in range(1,max_ngram+1):
                    if(i+n <= len(words_line_clean)):
                        ngram = u"+".join(words_line_clean[i:i+n])
                        #word_count
                        count = ngram_counts.get(ngram)
                        if count is None:
                            ngram_counts.update({ngram:1})
                        else:
                            ngram_counts.update({ngram:count+1})

    for key, value in sorted(ngram_counts.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        out.write("%s\t%s\n" % (key.encode('utf-8'), value))
    out.close()

if __name__ == '__main__':
    # pdf2txt
    if not os.path.exists(pdf2txt_dir):
        os.makedirs(pdf2txt_dir)
    for f in files:
        pdf2txt(["pdf2txt.py","-o",pdf2txt_dir+f.split(".")[0]+".txt",material_dir+f.split(".")[0]+".pdf"])
    # txt2grams
    if not os.path.exists(gramcount_dir):
        os.makedirs(gramcount_dir)
    for f in files:
        txt2grams(pdf2txt_dir+f.split(".")[0]+".txt",gramcount_dir+f.split(".")[0]+"_gramcount.txt")
    # tfidf
    if not os.path.exists(tfidf_dir):
        os.makedirs(tfidf_dir)
    for f in files:
        gram_tfidf = {}
        fname = gramcount_dir + f.split(".")[0]+"_gramcount.txt"
        with open(fname,'r') as text_file:
            fout = open(tfidf_dir + f.split(".")[0]+"_tfidf.txt","w")
            for line in text_file:
                word,tf = line.split("\t");
                #count idf
                docfreq = 0
                for fs in files:
                    fname = gramcount_dir + fs.split(".")[0]+"_gramcount.txt"
                    if word in open(fname,'r').read():
                        docfreq += 1
                idf = math.log(len(files)/docfreq,2)
                gram_tfidf.update({word:int(tf)*idf})

        for key, value in sorted(gram_tfidf.iteritems(), key=lambda (k,v): (v,k), reverse=True):
            fout.write("%s\t%s\n" % (key, value))
        fout.close()
    #TF.IDF  Round1
    if not os.path.exists(tfidf_com_dir):
        os.makedirs(tfidf_com_dir)
    for f in files:
        with open(tfidf_dir + f.split(".")[0]+"_tfidf.txt",'r') as text_file:
            fout = open(tfidf_com_dir + f.split(".")[0]+"_tfidf_com1.txt","w")
            old_word, old_tfidf = text_file.readline().strip().split("\t")
            for line in text_file:
                word, tfidf = line.strip().split("\t")
                if(tfidf==old_tfidf):
                    if(old_word in word): old_word = word
                    elif(word in old_word): continue
                    else:
                        fout.write("%s\t%s\n" % (old_word,old_tfidf))
                        old_word, old_tfidf = word, tfidf
                else:
                    fout.write("%s\t%s\n" % (old_word,old_tfidf))
                    old_word, old_tfidf = word, tfidf
    #TF.IDF Round2
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    for f in files:
        word_tfidf = {}
        with open(tfidf_com_dir + f.split(".")[0]+"_tfidf_com1.txt",'r') as text_file:
            fout = open(result_dir + f.split(".")[0]+".txt","w")

            #read file into dic
            for line in text_file:
                word, tfidf = line.strip().split("\t")
                word_tfidf.update({word:tfidf})

            #scan dic and compare items
            delete_list = []
            for item in word_tfidf:
                word_tfidf.update({item:float(word_tfidf.get(item)) + (float(word_tfidf.get(item))*(len(item.split("+"))-1)*0.5)})

            pattern_ch = u'[\u4e00-\u9fa5]+'
            pattern_en = u'[A-Za-z]+'
            pattern_mark = u'[/]+'
            pattern_num = u'[0-9]+\.[0-9]+'
            key_list = word_tfidf.keys()
            for i in range(len(word_tfidf)):
                key_line = key_list[i].split("+")
                new_key = ""
                last_word = ""
                for word in key_line:
                    if(re.match(pattern_ch,unicode(last_word,"utf-8"))):
                        if(re.match(pattern_en,unicode(word,"utf-8")) or re.match(pattern_num,unicode(word,"utf-8"))):
                            new_key += (" " + word)
                        else:
                            new_key += word
                    elif(re.match(pattern_en,unicode(last_word,"utf-8")) or re.match(pattern_num,unicode(last_word,"utf-8"))):
                        if(re.match(pattern_mark,unicode(word,"utf-8"))):
                            new_key += word
                        else:
                            new_key += (" " + word)
                    elif(re.match(pattern_mark,unicode(last_word,"utf-8"))): # /
                        new_key += word
                    else: #first word
                        new_key += word
                    last_word = word

                word_tfidf[new_key]=word_tfidf.pop(key_list[i])
                #word_tfidf.update({new_key:word_tfidf.get(item)})
                #word_tfidf.pop(item)
                #fout.write("%s\t%s\n" % (new_key, value))

            for item1 in word_tfidf:
                for item2 in word_tfidf:
                    if(item1 in item2):
                        if(word_tfidf.get(item1) < word_tfidf.get(item2)):
                            if(item1 not in delete_list):delete_list.append(item1)
                        elif(word_tfidf.get(item1) > word_tfidf.get(item2)):
                            if(item2 not in delete_list):delete_list.append(item2)
                        else: #judge if self or not
                            if(len(item1) > len(item2) and item2 not in delete_list):delete_list.append(item2)
                            elif(len(item1) < len(item2) and item1 not in delete_list):delete_list.append(item1)
                            else:continue

            #remove items
            for item in delete_list:
                #print item
                word_tfidf.pop(item)

            #string to float
            for item in word_tfidf:
                word_tfidf.update({item:float(word_tfidf.get(item))})

            #output result
            for key, value in sorted(word_tfidf.iteritems(), key=lambda (k,v): (v,k), reverse=True):
                fout.write("%s\t%s\n" % (key, value))
