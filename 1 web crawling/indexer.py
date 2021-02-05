import os, json
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import Counter
from collections import defaultdict


ps = PorterStemmer()    # stemming for better textual match
tokenizer = RegexpTokenizer(r'\w+')             # tokenize
stop_words = set(stopwords.words('english'))    # stop words
# url_doc_count = dict()  # for doc name/id the token was found in
# word_count = dict()     # for total word count
# bold_count = dict()     # for bold word only
# head_count = dict()     # for header word only
# title_count = dict()    # for title word only

class Posting:
    def __init__(self):
        self.doc_set = set()
        self.freq = Counter()
        self.bold_count = Counter()
        self.head_count = Counter()
        self.title_count = Counter()

    # counter how many document .
    def add(self, doc_index, token_type = ''):
        self.freq[doc_index] += 1
        if token_type == 'head':
            self.head_count[doc_index] += 1
        if token_type == 'bold':
            self.bold_count[doc_index] += 1
        if token_type == 'title':
            self.title_count[doc_index] += 1
        self.doc_set.add(doc_index)

    # total word counter
    def get_freq(self, doc_index):
        return self.freq[doc_index]

    def get_bold_freq(self, doc_index):
        return self.bold_count[doc_index]

    def get_head_freq(self, doc_index):
        return self.head_count[doc_index]

    def get_url_indexes(self):
        return self.doc_set.copy()

    def intersect(self, other_posting):
        result = Posting()
        result.doc_set = self.doc_set.intersection(other_posting.doc_set)
        for i in result.doc_set:
            result.bold_count[i] = self.bold_count[i] + other_posting.bold_count[i]
            result.head_count[i] = self.head_count[i] + other_posting.head_count[i]
            result.title_count[i] = self.title_count[i] + other_posting.title_count[i]
            result.freq[i] = self.freq[i] + other_posting.freq[i]
        return result

    def __str__(self):
        return str(self.doc_set)


class DocumentInfo:
    def __init__(self, url, num_tokens):
        self.url = ''
        self.tokens_in_document = 0

url_list = []
inverted_index = defaultdict(Posting) 


# https://www.tutorialspoint.com/python/os_walk.htm
def read_json_file(directory):
    doc_count = 0       
    for root, dirs, files in os.walk(directory):
        for file in files:
            get_file = os.path.join(root, file)
            if get_file.endswith('.json'):
                read_file = open(get_file, encoding='utf-8').read()
                file_content = json.loads(read_file)
                try:
                    json_content = file_content['content']  # get contents
                    json_url = file_content['url']          #url
                    url_list.append(json_url)                   # url_list  
                    # url_doc_count[doc_count] = json_url
                    doc_count += 1
                    tokenize(json_content, len(url_list) - 1)
                    
                except(json.JSONDecodeError):
                    print("This is not json file --> " + get_file)
    #print(doc_count) -> 55393

# all alphanumeric 
def tokenize(contents, url_index):
    soup = BeautifulSoup(contents, 'html.parser')
    #print(soup.prettify())
        
    # b, strong
    #print("*Tag: <b>")
    for bold in soup.find_all(['b', 'strong']):
        for word in tokenizer.tokenize(bold.text):
            word = ps.stem(word.lower())
            inverted_index[word].add(url_index, 'bold')
            #inverted_index["cat"].add ( document #3, type = bold )


    # headings - h1, h2, h3
    #print("*Tag: <h>")
    for heading in soup.find_all(['h1', 'h2', 'h3']):
        for word in tokenizer.tokenize(heading.text):
            word = ps.stem(word.lower())
            inverted_index[word].add(url_index, 'head' )


    # title
    #print("*Tag: <title>")
    for title in soup.find_all(['title']):
        for word in tokenizer.tokenize(title.text):
            word = ps.stem(word.lower())
            inverted_index[word].add(url_index, 'title')
            
    # each_document [ word_count, ]

def make_counter(word_dic):
    c = Counter(word_dic)
    top = dict(c.most_common())
    #print(top)
    return top
    #return c

def search(*words):
    posting = inverted_index[ps.stem(words[0])]
    for word in words[1:]:
        word = ps.stem(word.lower())
        posting = posting.intersect(inverted_index[word])
        
    for i in posting.get_url_indexes():
        print(url_list[i])

if __name__ == '__main__':
    directory = os.getcwd()
    read_json_file(directory)
    print("Reading json file DONE")

    search('machine', 'learning')

    #print inverted _ index 
    # print ( inverted_index )

    # # how can see total tokens 
    # print ( len(inverted_index))
    # print ( inverted_index )
    # how we can see the document page number 


    # bold_count
    # with open('bold_count.json', 'w') as bold_count_json :
    #     print("Processing words in bold tag")
    #     json.dump(make_counter(bold_count), bold_count_json)
    # # header_count
    # with open('header_count.json', 'w') as header_count_json :
    #     print("Processing words in header tag")
    #     json.dump(make_counter(head_count), header_count_json)

    # # title_count
    # with open('title_count.json', 'w') as title_count_json :
    #     print("Processing words in title tag")
    #     json.dump(make_counter(title_count), title_count_json)

    # # word_count
    # with open('word_count.json', 'w') as word_count_json:
    #     print("Processing ttal word count")
    #     json.dump(make_counter(word_count), word_count_json)

    #     print ( "make_counter(word_count)", make_counter(word_count))
    #     print ( "type of make_counter(word_count) = ", type ( make_counter(word_count)))
    #     x = make_counter(word_count)
    #     print ( "heere ", x )
    # print("Processing DONE") 
