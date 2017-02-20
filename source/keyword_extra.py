import sys
import os

if len(sys.argv) < 4:
    print('Usage: python3 [].py type week1 slide_num book_num')
    sys.exit()
else:
    type_ = sys.argv[1]
    week_num = sys.argv[2]
    extra_slide = sys.argv[3]
    extra_book = sys.argv[4]

# using the file of the tfidf to get the top-n word
def select_keyword_1(path, extra_slide, out_path):
    with open(path, 'r') as fr:
        lines = fr.readlines()
    with open(out_path, 'w') as fw:
        for num in range(extra_slide):
            fw.write(lines[num])

def select_keyword_2(slide_path, book_path, extra_slide, extra_book, out_path):
    with open(slide_path, 'r') as fr_s:
        slide_lines = fr_s.readlines()
    with open(book_path, 'r') as fr_b:
        book_lines = fr_b.readlines()
    with open(out_path, 'w') as fw:
        for num in range(extra_slide):
            fw.write(slide_lines[num])
        for num in range(extra_book):
            fw.write(book_lines[num])

if __name__ == '__main__':
    slide_path = 'dict/slide/' + week_num + '.txt'
    book_path = 'dict/book/' + week_num + '.txt'
    write_path_slide = 'keyword-extra/slide/' + week_num + '.txt'
    write_path_combine = 'keyword-extra/slide_add_book/' + week_num + '.txt'
    extra_slide = int(extra_slide)
    if type_ == '1':
        select_keyword_1(slide_path, extra_slide, write_path_slide)
    elif type_ == '2':
        extra_book = int(extra_book)
        select_keyword_2(slide_path, book_path, extra_slide, extra_book, write_path_combine)
