from collections import Counter


class Posting:
    def __init__(self):
        self.doc_set = set()
        self.freq = Counter()           #Term frequent for a term in  a document 
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

    def get_num_docs(self):
        return len(self.doc_set)
    

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

    def __contains__(self, index):
        

        if type(index) == int:
            return index in self.doc_set


    