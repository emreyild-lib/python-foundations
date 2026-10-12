# review_insight_extractor.py

#pip install pandas
#pip install spacy
#pip install gensim
#pip install nltk
#pip install transformers
#python -m spacy download en_core_web_sm
#pip install --upgrade torch

# review_insight_extractor.py (Lightweight Version)

import pandas as pd
import spacy
import gensim
from gensim import corpora
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from transformers import pipeline

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load dataset
input_file = "customer_reviews_realistic.csv"
df = pd.read_csv(input_file)

# ------------------ Step 1: Named Entity Recognition (NER) ------------------
nlp = spacy.load("en_core_web_sm")

def extract_entities(text):
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]

df['Entities'] = df['Review_Text'].apply(extract_entities)
df[['Review_ID', 'Entities']].to_csv("named_entities.csv", index=False)

# ------------------ Step 2: Topic Modeling ------------------
def preprocess(text):
    tokens = word_tokenize(text.lower())
    return [word for word in tokens if word.isalpha() and word not in stopwords.words('english')]

df['Tokens'] = df['Review_Text'].apply(preprocess)

dictionary = corpora.Dictionary(df['Tokens'])
corpus = [dictionary.doc2bow(text) for text in df['Tokens']]

lda_model = gensim.models.LdaModel(corpus, num_topics=3, id2word=dictionary, passes=15)

def get_dominant_topic(doc_bow):
    return sorted(lda_model[doc_bow], key=lambda x: -x[1])[0][0]

df['Dominant_Topic'] = [get_dominant_topic(bow) for bow in corpus]
df[['Review_ID', 'Dominant_Topic']].to_csv("topic_modeling.csv", index=False)

# ------------------ Step 3: Text Summarization ------------------
# Use smaller model to avoid large download size and torch version issues
summarizer = pipeline("summarization", model="t5-small")

df['Summary'] = df['Review_Text'].apply(lambda x: summarizer(x, max_length=30, min_length=10, do_sample=False)[0]['summary_text'])
df[['Review_ID', 'Summary']].to_csv("summarized_reviews.csv", index=False)

# ------------------ Final Export ------------------
df.to_csv("review_insight_full_output.csv", index=False)
print("✅ All files saved: named_entities.csv, topic_modeling.csv, summarized_reviews.csv, review_insight_full_output.csv")
