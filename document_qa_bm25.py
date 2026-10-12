#pip install streamlit rank-bm25 transformers torch

# -------------------
# Import libraries
# -------------------
import re              # For cleaning text using regular expressions
import math            # (Not used here but normally for math functions)
import pathlib         # To work with file paths easily
from typing import List, Tuple  # For type hints (helps us define data types clearly)

import streamlit as st              # Streamlit for building the web app
from rank_bm25 import BM25Okapi     # BM25 for document retrieval (finding relevant text chunks)
from transformers import pipeline   # Hugging Face pipeline for Question-Answering models


# -------------------
# Helper Functions
# -------------------

def normalize_whitespace(text: str) -> str:
    # Cleans text by replacing multiple spaces/newlines with a single space
    return re.sub(r"\s+", " ", text).strip()

def split_into_chunks(text: str, target_words: int = 180, overlap_words: int = 20) -> List[str]:
    """
    Splits the document into smaller text chunks.
    Each chunk has about 'target_words' words with optional overlap for context.
    """
    words = normalize_whitespace(text).split()   # Clean text and split into words
    if not words:
        return []   # If no words, return empty list

    chunks = []     # This will store all text chunks
    step = max(1, target_words - overlap_words)   # Step size to slide over words
    for start in range(0, len(words), step):
        end = min(len(words), start + target_words)   # End position of the chunk
        chunk_words = words[start:end]                # Extract chunk
        if len(chunk_words) < max(20, target_words // 4) and chunks:
            # If last chunk is too small, merge it with the previous one
            chunks[-1] += " " + " ".join(chunk_words)
            break
        chunks.append(" ".join(chunk_words))  # Add the chunk to the list
        if end == len(words):  # Stop if we reached the end
            break
    return chunks


def bm25_prepare(corpus_chunks: List[str]) -> Tuple[BM25Okapi, List[List[str]]]:
    # Prepares BM25 retriever by tokenizing all chunks (splitting into words)
    tokenized = [chunk.lower().split() for chunk in corpus_chunks]
    bm25 = BM25Okapi(tokenized)   # Initialize BM25 on the tokenized chunks
    return bm25, tokenized


def rank_chunks(bm25: BM25Okapi, tokenized_chunks: List[List[str]], query: str, top_k: int = 5) -> List[int]:
    # Finds top_k most relevant chunks for the query using BM25 scores
    q_tokens = query.lower().split()          # Tokenize the user query
    scores = bm25.get_scores(q_tokens)        # BM25 gives a relevance score for each chunk
    top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return top_idx   # Return indices of top scoring chunks


def make_qa_reader(model_name: str = "deepset/roberta-base-squad2"):
    # Creates a Question-Answering model pipeline from Hugging Face
    return pipeline("question-answering", model=model_name, tokenizer=model_name)


def run_reader_on_chunks(reader, question: str, chunks: List[str], per_chunk_top_n: int = 1):
    """
    Runs the QA model on each chunk.
    Returns answers with confidence scores and context for each chunk.
    """
    results = []
    for c in chunks:
        out = reader(question=question, context=c)  # Ask the question on each chunk
        ans = {
            "answer": out.get("answer", ""),      # Extract answer text
            "score": float(out.get("score", 0.0)),# Extract confidence score
            "context": c,                         # The chunk where the answer was found
        }
        results.append(ans)
    # Sort answers by confidence score in descending order
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# -------------------
# Streamlit Web App Interface
# -------------------

st.set_page_config(page_title="📊 Business Insight Extractor (BM25 + QA)", page_icon="📊", layout="centered")
# Above sets page title, tab icon, and layout style

st.title("📊 Business Insight Extractor (No-Haystack)")
st.write("Upload a business report (.txt), ask a question, and get **extractive** answers.")


# -------------------
# Upload business report or use default text
# -------------------
uploaded_file = st.file_uploader("Upload a business report (.txt)", type=["txt"])
if uploaded_file:
    text = uploaded_file.read().decode("utf-8", errors="ignore")   # Read uploaded file
else:
    st.info("Using default sample report from ./data/sample_report.txt")
    default_path = pathlib.Path("data/sample_report.txt")
    if default_path.exists():
        text = default_path.read_text(encoding="utf-8", errors="ignore")   # Read default file if exists
    else:
        # If no file found, use fallback text
        text = (
            "Q3 Business Report: Revenue increased by 12% YoY. "
            "Primary drivers were subscription upgrades and reduced churn in EMEA. "
            "Risks include supply chain delays and currency fluctuations. "
            "Mitigation includes dual sourcing and natural hedging."
        )


# -------------------
# Preview the loaded text
# -------------------
st.text_area("Document Preview", value=text, height=220)   # Show text in scrollable box


# -------------------
# Sliders for parameters
# -------------------
col1, col2, col3 = st.columns(3)   # Three columns layout
with col1:
    chunk_words = st.slider("Chunk size (words)", 100, 400, 180, 10)  # Words per chunk
with col2:
    overlap_words = st.slider("Overlap (words)", 0, 80, 20, 5)        # Overlap between chunks
with col3:
    retriever_top_k = st.slider("Retriever top_k", 1, 10, 5, 1)       # How many chunks to retrieve

# Text box for user query
query = st.text_input("Ask a question (e.g., 'What are the risks?')")


# -------------------
# Prepare chunks and BM25 retriever
# -------------------
chunks = split_into_chunks(text, target_words=chunk_words, overlap_words=overlap_words)
if not chunks:
    st.warning("No text to process.")
    st.stop()

bm25, tokenized_chunks = bm25_prepare(chunks)


# -------------------
# Model selection dropdown
# -------------------
model_name = st.selectbox(
    "Reader model",
    ["deepset/roberta-base-squad2", "distilbert-base-cased-distilled-squad"],  # Choose between two models
    index=0,
)


# -------------------
# Run QA pipeline on button click
# -------------------
if st.button("🔍 Get Insight") and query:
    with st.spinner("Retrieving relevant passages and reading answers..."):
        # Step 1: Retrieve top chunks
        top_idx = rank_chunks(bm25, tokenized_chunks, query, top_k=retriever_top_k)
        retrieved = [chunks[i] for i in top_idx]

        # Step 2: Run QA model on retrieved chunks
        reader = make_qa_reader(model_name=model_name)
        answers = run_reader_on_chunks(reader, query, retrieved, per_chunk_top_n=1)

    # Step 3: Display answers or warning
    if answers:
        for i, a in enumerate(answers, 1):
            st.markdown(f"### Answer {i}")
            st.markdown(f"**Text:** {a['answer']}")
            st.markdown(f"**Score:** {a['score']:.4f}")   # Show confidence score
            with st.expander("Show context"):
                st.write(a["context"])   # Show chunk where answer was found
            st.markdown("---")
    else:
        st.warning("No relevant answers found. Try adjusting chunk size or your question.")
