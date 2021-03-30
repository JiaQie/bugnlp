import pandas as pd
import bugReportTokenizer as brt
import collections as c
tokenizer = brt.BugReportTokenizer()

test = pd.read_csv('/Users/jiaqie/Desktop/CiscoHacks/mozilla_firefox.csv')

tokenset = []


test['tokenized'] = test['Description'].apply(lambda Description:tokenizer.tokenize(Description, lower = True,n_grams = 2,remove_stop_words = True,remove_english_words = True))


for doc in test['tokenized']:
    for token in doc:
        tokenset.append(token)

counts = c.Counter(tokenset)

top_bigrams = counts.most_common(1000)

bigrams = {}
for pair in top_bigrams:
    bigrams[pair[0]] = pair[0]

rels = []


for bigram_one in bigrams.keys():       
    for bigram_two in bigrams:
        coin = []
        for token in report:
            if bigrams.get(token,'') != '':
                coin.append(token)
        rels.append(coin)
        

pd.DataFrame(bigrams.keys(),columns = ['name']).to_csv('bigrams.csv')
pd.DataFrame(rels).to_csv('coincide.csv')

    
