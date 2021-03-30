from nltk.corpus import words
from string import punctuation
from collections import Counter
import numpy as np
import math
import re 
w = words.words()
eng = {}
for word in w:
    eng[word] = word
 
 
    
#### want something that picks up common key words 
## add n-gram functionality with tf-igm feature selection
## 1 - 5 gram    
class BugReportTokenizer(object):
    
    def __init__(self,encoding = 'utf=8',punctuation = punctuation):
        self._encoding = encoding
        self._punc = r"(?:|'|!+|,|\.|;|:|\(|\)|-\"|\?+)?"  
        self._stop = ('ourselves','hers','between','yourself','but','again','there','about','once','during','out',	
                      'very','having','with','they','own','an','be','some','for','do','its','yours','such','into','of',	
                      'most','itself','other','off','is','s','am','or','who','as','from','him','each','the','themselves',	
                      'until','below','are','we','these','your','his','through','don','nor','me','were','her','more',	
                      'himself','this','down','should','our','their','while','above','both','up','to','ours','had',	
                      'she','all','no','when','at','any','before','them','same','and','been','have','in','will','on',
                      'does','yourselves','then','that','because','what','over','why','so','can','did','not','now',	
                      'under','he','you','herself','has','just','where','too','only','myself','which','those','i','after',	
                      'few','whom','t','being','if','theirs','my','against','a','by','doing','it','how','further',	
                      'was','here','than')

    
    def tokenize(self,s,lower = False,remove_english_words = False,remove_stop_words = False,n_grams = 1):
        tokens = []
        s = str(s)
        for word in s.split():
            word = word.strip(self._punc)
            word = ' '.join(word.split(punctuation))
            for i in range(len(word)):
                if i == 0 or i == len(word) - 1:
                    if word[i] in self._punc:
                        word = word.replace(word[i],' ')
                else:
                    if word[i] in self._punc:
                        if word[i-1] in self._punc or word[i+1]  in self._punc:
                            word = word.replace(word[i],' ')
            word = word.strip()
            self._stop = self._stop if remove_stop_words else []
            eng_words = eng if remove_english_words else {}
            if lower:
                tokens.extend([w.lower() for w in word.strip().split() if w not in self._stop and eng_words.get(w,'') == ''])
            else:
                tokens.extend([w for w in word.strip().split() if w not in self._stop and eng_words.get(w,'') == ''])

        return self.n_grams(tokens,n_grams)

    def n_grams(self,tokens,n_grams = 1):
        final = []
        if n_grams > 1:
            tokens.insert(0,'START')
            tokens.insert(len(tokens),'END')
        for i in range(len(tokens)):
            gram = tokens[i]
            for j in range(1,n_grams):
                if i + j <len(tokens):
                    gram = gram + "/" + tokens[i+j]
            if gram.count("/") == n_grams - 1:
                final.append(gram)
        return final
    
    def feature_selection(self,documents,tokens):
        lamb = 7
        regTokens = []
        noRegTokens = []
        results = []
        reg = documents[documents['class'] == 1]
        noReg = documents[documents['class'] == 0]
        for report in reg['out']:
            regTokens.extend(report)
        for report in noReg['out']:
            noRegTokens.extend(report)
        regCounts = Counter(regTokens)
        noRegCounts = Counter(noRegTokens)
        for token in tokens:
            regcount = regCounts[token]
            noRegcount = noRegCounts[token]
            igm = 1 + (lamb*(max(regcount,noRegcount)/(max(regcount,noRegcount) + 2*min(regcount,noRegcount))))
            results.append((igm,token * math.sqrt(regcount + noRegcount)))
        return results
            
    def populate_term_index(self,term_index,tokens):
        i = len(term_index)
        for token in tokens:
            term_index[token] = i
            i += 1
        
    def dense_encode(self,report,term_index):
        vec = np.zeros(len(report),dtype=int)
        for i,word in enumerate(report):
            vec[i] = term_index.get(word,0)
        return vec
    
    def one_hot_encode(self,report,tokens,term_index):
        mat = np.zeros([len(tokens)])
        encoded_report = self.dense_encode(report,term_index)
        mat[encoded_report] = 1
        return mat
    
    
if __name__ == '__main__':
    import time
    import pandas
    a = time.time()
    tokenizer = BugReportTokenizer()
    df = pandas.read_csv('tokenizerTest.csv')
    df['with'] = df['report'].apply(lambda report:tokenizer.tokenize(report, lower = True,n_grams = 1))
    df['out'] = df['report'].apply(lambda report:tokenizer.tokenize(report, lower = True,n_grams = 1, remove_english_words = True))
    df[['with','out']].to_csv('tokenResults.csv')
    print(time.time() - a)
   
