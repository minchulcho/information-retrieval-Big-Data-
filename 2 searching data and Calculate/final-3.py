import os, json, math, time
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from collections import Counter
from collections import defaultdict
from Posting import Posting
import pickle


ps = PorterStemmer()                                    # stemming for better textual match
tokenizer = RegexpTokenizer(r'\w+')                     # tokenize
stop_words = set(stopwords.words('english'))            # stop words

url_list = []
inverted_index = defaultdict(Posting)                   # inverted_index ==> dictionary and keys are words and values are Posting objects 
totalNumOfDoc = 55393
total_docs = 0

class DocumentInfo:
    def __init__(self, url = '', num_tokens = 0):
        self.url = url
        self.tokens_in_document = num_tokens

    def inc_token_count(self):
        self.tokens_in_document += 1

    def get_url(self):
        return self.url

    def get_num_tokens(self):
        return self.tokens_in_document

def read_json_file(directory):
    pickle_file = open("./pickle_file", 'wb')           # Using "wb", we need also dump the url_list , 
                                                        # open pickle file here. Previous put this in "tokenize" but it was wrong. this is right place  
    global total_docs
    for root, dirs, files in os.walk(directory):
        for file in files:
            get_file = os.path.join(root, file)
            if get_file.endswith('.json'):
                read_file = open(get_file, encoding='utf-8').read()
                file_content = json.loads(read_file)
                try:
                    json_content = file_content['content']  
                    json_url = file_content['url']          # url
                    if json_url.find('#') == -1 and json_url.find('https://www.ics.uci.edu/~eppstein/pix') == -1 and json_url.find('format=xml') == -1:            # exclude frag(#)
                        url_list.append(DocumentInfo(url = json_url))
                        total_docs += 1
                        tokenize(json_content, len(url_list)-1 )
                    
                except(json.JSONDecodeError):
                    print("This is not json file --> " + get_file)

    pickle.dump(url_list,  pickle_file)                         #   Dumping to pickle_file, url_list 
    pickle.dump(inverted_index, pickle_file)                    #   Dumping to pickle_file, inverted_index
    pickle.dump(total_docs, pickle_file)                        #   Dumping to pickle_file, total_docs
    pickle_file.close( )                                        #   close. if not close file, picklie_file delete error. 

def tokenize(contents, url_index):
    soup = BeautifulSoup(contents, 'html.parser')
    for bold in soup.find_all(['b', 'strong']):
        for word in tokenizer.tokenize(bold.text):
            url_list[url_index].inc_token_count()
            word = ps.stem(word.lower())
            inverted_index[word].add(url_index, 'bold')         # store key and add document to posting 

    for heading in soup.find_all(['h1', 'h2', 'h3']):
        for word in tokenizer.tokenize(heading.text):
            url_list[url_index].inc_token_count()
            word = ps.stem(word.lower())
            inverted_index[word].add(url_index, 'head' )        # store key and add document to posting 

    for title in soup.find_all(['title']):
        for word in tokenizer.tokenize(title.text):
            url_list[url_index].inc_token_count()
            word = ps.stem(word.lower())
            inverted_index[word].add(url_index, 'title')        # store key and add document to posting 
    # dump to pickle 

def print_inverted_index ():
    #print("printing whole list start here")
    for key, posting in inverted_index.items():
        print ( (key, [(url_list[i].get_url(), posting.get_freq(i)) for i in posting.get_url_indexes()]))


def get_least_common() :    # function to get least common 20 queries
    least = list(inverted_index.keys())[:-21:-1]
    return least

def term_freq(posting, doc_index):
    return posting.get_freq(doc_index)

def doc_freq(posting):
    return posting.get_num_docs()
 
def terms_in_doc(doc_index):
    return url_list[doc_index].get_num_tokens()

def tf_idf_score(posting, doc_index):
    #print ( "term_freq(posting, doc_index) " , term_freq(posting, doc_index))
    #print ( "terms_in_doc(doc_index) ", terms_in_doc(doc_index))
    #print ( "total_docs = ", total_docs)
    #print ("  doc_freq(posting) ", doc_freq(posting))
    return (1 + math.log10(term_freq(posting, doc_index) ) )  * math.log10(total_docs/doc_freq(posting))

def query_score(words, doc_index):
    return sum([tf_idf_score(inverted_index[w], doc_index) for w in words if doc_index in inverted_index[w]])

def cosineScore(user_input, ntop):
    user_input = [ps.stem(w) for w in user_input.split()]
    qn = len(user_input)                                    # counter user input 

    if not user_input:
        return None

    scores = defaultdict(float)                             # create scores 

    for term in user_input:                         
        posting = inverted_index[term]                      # insert the term in inverted_index 
        w_tq = 1 + math.log10(user_input.count(term)/qn)           # cal W(tq)
        for d in posting.get_url_indexes():                     # d = document , w = word 
            w_td = term_freq(posting, d)        
            scores[d] += w_td * w_tq                        # score = TF-IDF score *  frequency of the target term in the query 

    for k,v in scores.items():
        scores[k] = v/url_list[k].get_num_tokens()      # nornalization = score divied "number of term in document"

    return sorted(scores.items(), key = lambda p: p[1], reverse = True)[:ntop]
    



def search(user_input, show_score = False):
    user_input = [ps.stem(w) for w in user_input.split()]

    if not user_input:
        return None

    doc_set = set()
    for w in user_input:
        posting = inverted_index[w]
        doc_set = doc_set.union(posting.get_url_indexes())

    if show_score:
        ranking = [(i, query_score(user_input, i)) for i in doc_set]
        ranking = sorted(ranking, key = lambda x: x[1], reverse = True)
        ranking = [(url_list[i].get_url(), s) for i, s in ranking]                      # url list and score 
    else:
        ranking = sorted(doc_set, key = lambda x: query_score(user_input, x), reverse = True)
        ranking = [url_list[i].get_url() for i in ranking]                              # url list 
    #print (ranking)
    return ranking

if __name__ == '__main__':
    directory = os.getcwd()
    if os.path.isfile('./pickle_file'):
        with open('./pickle_file', 'rb') as pickle_file:                            
            url_list = pickle.load(pickle_file)
            inverted_index = pickle.load(pickle_file)
            total_docs = pickle.load(pickle_file)
    else:
        read_json_file(directory)
        print("Reading json file DONE")

    # print(url_list[:5])
    # print(list(inverted_index.keys())[:5])

    # print("List of 20 least common queries: ", get_least_common())
    
    #print_inverted_index()
    user_input = input("Enter search query: ")
    start_time = time.time_ns() # start to calculate run time
    
    tf_idf_result = search(user_input, True) 

    end_time = time.time_ns()
    running_time = (end_time - start_time) / (10**6)

    for url, score in tf_idf_result:                             
        print(url, score)

    start_time = time.time_ns() # start to calculate run time
    results = cosineScore(user_input, 20)  # second = top 20 sorted , how many result we want . 
    end_time = time.time_ns()
    running_time = (end_time - start_time) / (10**6)
    

    print ( " ###################################################################################### \n")
    for index, score in results:                             
        print(url_list[index].get_url(), score)

    print("Response to search query : ", running_time, " ms")

    
    #########################################
    # Don't delete print_inverted_index()
    # This method "print_inverted_index", we can see inverted index table. 
    # key = word. value = [url, frequency]
    # print_inverted_index()
    


# Searching query example.    
# Artificial Intelligence
# cristina lopes.
# machine learning
# ACM
# master of software engineering


# List of TOP 10 common queries:  ['the', 'transform', 'play', 'lab', 'class', 'fall', '2019', 'winter', '2020', '2018', '2017']
 
#['sourcerercc', 'déjàvu', '7gb', '1gb', '54gb', '3gb', 'multilabel', 'clonedetect', 'hobbes2', 'unalign', 'popcnt', 'papalexaki', 'pujara', 'yangfeng', 'multiag', 'shufeng', 'subreddit', 'uciml', 'doroudi', 'shayan']