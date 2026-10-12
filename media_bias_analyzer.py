import streamlit as st
import pandas as pd
import requests
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

# Initialize VADER analyzer
vader = SentimentIntensityAnalyzer()

# Function to fetch headlines
def get_headlines(source, api_key):
    url = f"https://newsapi.org/v2/top-headlines?sources={source}&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    headlines = [article["title"] for article in data["articles"]]
    return headlines

# Function to analyze sentiment
def analyze_sentiment(text):
    blob = TextBlob(text)
    vader_score = vader.polarity_scores(text)
    return blob.sentiment.polarity, vader_score['compound']

# Streamlit App UI
st.set_page_config(page_title="📰 Media Bias Analyzer", layout="wide")
st.title("📰 AI-Powered Media Bias Analyzer")

api_key = st.text_input("Enter your NewsAPI Key:", type="password")

# Real news sources
sources = {
    "CNN": "cnn",
    "BBC News": "bbc-news",
    "Fox News": "fox-news"
}

if api_key:
    all_data = []
    for source_name, source_code in sources.items():
        headlines = get_headlines(source_code, api_key)
        for headline in headlines:
            blob_score, vader_score = analyze_sentiment(headline)
            all_data.append({
                "Headline": headline,
                "Source": source_name,
                "TextBlob Sentiment": blob_score,
                "VADER Sentiment": vader_score
            })

    df = pd.DataFrame(all_data)

    st.subheader("📊 Sentiment Analysis Result")
    st.dataframe(df)

    st.subheader("📈 Average Sentiment by News Source")
    avg_sent = df.groupby("Source")[["TextBlob Sentiment", "VADER Sentiment"]].mean()

    # Show Streamlit chart
    st.bar_chart(avg_sent)

    # Show clearer, labeled matplotlib chart
    st.subheader("🎯 Clear Tone Analysis (TextBlob Sentiment)")
    fig, ax = plt.subplots(figsize=(8, 5))
    sentiment_scores = avg_sent["TextBlob Sentiment"]
    bars = ax.bar(sentiment_scores.index, sentiment_scores.values)

    # Color bars and add interpretation labels
    colors = ['green' if val > 0 else 'gray' if val == 0 else 'red' for val in sentiment_scores]
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    for idx, val in enumerate(sentiment_scores.values):
        label = (
            "Mildly Positive" if val > 0 else
            "Neutral" if val == 0 else
            "More Negative"
        )
        ax.text(idx, val + 0.02 if val >= 0 else val - 0.07,
                f"{label}\n({val:.2f})", ha='center', va='center', fontsize=10)

    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_ylabel("Average TextBlob Sentiment")
    ax.set_ylim(-0.6, 0.4)
    ax.set_title("Emotional Tone Comparison Across News Sources")
    st.pyplot(fig)

else:
    st.warning("Please enter your NewsAPI key to fetch headlines.")
