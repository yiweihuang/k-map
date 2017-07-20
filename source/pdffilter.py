# -*- Encoding: UTF-8 -*-
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox,LTChar, LTFigure, LTAnno
from pdfminer.converter import PDFPageAggregator
import pdfminer
import re
import json
import codecs
import sys
import math
# Open a PDF file.
print sys.argv[1]
FILENAME = sys.argv[1]
print FILENAME+'.pdf'
fp = open('../invest/'+FILENAME+'.pdf', 'rb')
#chinses range : \u4e00-\u9fa5
#space : \s
#\uFF0C : full width comma
#\uFF1A : full width colon
#\uFF1B : full width semicolon
#\uFF0E : full width stop
#\u2215 : division slash
#\u003A : colon
#\uFF0D : Full width Hyphen-minus
#\u002D : Hyphen-minus
#\u2044 : fraction slash
#\u002B : plus
#\uFF09:full width right parenthesis
#\uFF08:left
#\u2022:bullet
#\u3001 : Chinese comma
pattern = u'[a-zA-Z0-9_\u4e00-\u9fa5\s\uFF08\uFF09\uFF65\u2022\uFF1A\uFF0C\u3001]'
# Create a PDF parser object associated with the file object.
parser = PDFParser(fp)

# Create a PDF document object that stores the document structure.
# Password for initialization as 2nd parameter
document = PDFDocument(parser)

# Check if the document allows text extraction. If not, abort.
if not document.is_extractable:
    raise PDFTextExtractionNotAllowed

# Create a PDF resource manager object that stores shared resources.
rsrcmgr = PDFResourceManager()

# Create a PDF device object.
device = PDFDevice(rsrcmgr)

# BEGIN LAYOUT ANALYSIS
# Set parameters for analysis.
laparams = LAParams()

# Create a PDF page aggregator object.
device = PDFPageAggregator(rsrcmgr, laparams=laparams)

# Create a PDF interpreter object.
interpreter = PDFPageInterpreter(rsrcmgr, device)
OutputDict = {}
def detect_specail_word(word):
    special_word = ['/','-',' ','+','：',':','(',')']
    #print word
    if word in special_word:
        return True
    else:
        return False

def parse_obj(lt_objs,pageNo):
    # loop over the object list
    isfirst        = True
    isfirstContent = False
    Layer          = 1
    lastX          = []
    layer          = []
    Info           = []
    for tbox in lt_objs:
        # if it's a textbox, print text and location
        tempString = ""
        if isinstance(tbox, pdfminer.layout.LTTextBoxHorizontal):
            nowX = tbox.bbox[0]
            #--------算averageSize
            for obj in tbox:
                tempString = ""
                averageSize=0
                length = 0

                for c in obj:
                    if (not isinstance(c, LTChar)) and (not isinstance(c, LTAnno)):
                        continue
                    tmp = c.get_text()
                    if re.match(pattern, tmp) is not None or detect_specail_word(tmp)==True:
                        if isinstance(c, LTAnno):
                            tempString+=c.get_text()
                        else:
                            length +=1
                            averageSize+=round(c.size)
                            tempString+=tmp
                    # else:
                    #     print tmp

                if length==0:
                    averageSize = averageSize/1
                else:
                    averageSize = math.floor(averageSize/length)
                #--------算averageSize
                same = False
                for index in range(len(lastX)):
                    if lastX[index] == nowX:
                        Info.append((tempString.replace('\n',' '),layer[index],averageSize))
                        lastX.append(nowX)
                        layer.append(layer[index])
                        same = True
                        break
                if same == False:
                    Info.append((tempString.replace('\n',' '),Layer,averageSize))
                    lastX.append(nowX)
                    layer.append(Layer)
                    Layer += 1
        # if it's a container, recurse
        elif isinstance(tbox, pdfminer.layout.LTFigure):
            parse_obj(tbox._objs,pageNo)
        isfirst = False
    ObjNo = {}
    for x in range(len(Info)):
        temp = {}
        temp['Content']=Info[x][0]
        temp['Layer']=Info[x][1]
        temp['Size']=Info[x][2]
        ObjNo[x+1] = temp

    OutputDict[pageNo]=ObjNo
def main():
    # loop over all pages in the document
    pageNo = 1
    ## for page in doc:
    for page in PDFPage.create_pages(document):
        # print (pageNo)
        sys.stdout.write('Page--- (' + str(pageNo) + ')\r')
        sys.stdout.flush()    # read the page into a layout object

        interpreter.process_page(page)
        layout = device.get_result()

        # extract text from this object
        parse_obj(layout._objs,pageNo)
        pageNo +=1

    with codecs.open('../done/'+FILENAME+"_with_Layer.json", 'w', encoding='utf-8') as f:
        json.dump(OutputDict, f, ensure_ascii=False)

if __name__=='__main__':
    main()
