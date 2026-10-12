
import nltk

import spacy

import string

from nltk.corpus import stopwords

from nltk.tokenize import word_tokenize

from nltk.stem import PorterStemmer

# --- Download resources (only needed the first time) ---

nltk.download('punkt')

nltk.download('punkt_tab')  # required for newer NLTK versions

nltk.download('stopwords')

# --- Load spaCy model ---

nlp = spacy.load("en_core_web_sm")

# --- Sample text ---

text = "Running faster than ever, the athlete exclaimed: 'Wow! What a race.'"

# 1. Lowercase and remove punctuation

text = text.lower()

text = text.translate(str.maketrans('', '', string.punctuation))

# 2. Tokenization

tokens = word_tokenize(text)

# 3. Remove stop words

filtered_tokens = [word for word in tokens if word not in stopwords.words('english')]

# 4. Stemming with NLTK

stemmer = PorterStemmer()

stemmed = [stemmer.stem(word) for word in filtered_tokens]

# 5. Lemmatization with spaCy

doc = nlp(' '.join(filtered_tokens))

lemmatized = [token.lemma_ for token in doc]

# --- Output results ---

print("Original Tokens:", tokens)

print("Filtered (No Stop Words):", filtered_tokens)

print("After Stemming:", stemmed)

print("After Lemmatization:", lemmatized)

