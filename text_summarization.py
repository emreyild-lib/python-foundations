# pip install --upgrade torch transformers accelerate sentencepiece
#pip install -U transformers accelerate sentencepiece safetensors

from transformers import pipeline
import textwrap

# Load summarization pipeline (CPU mode to avoid accelerate errors)
summarizer = pipeline(
    "summarization",
    model="Falconsai/text_summarization",
    device=-1  # CPU only; change to device_map="auto" if accelerate installed
)

def summarize_long_text(text, chunk_size=300, max_new_tokens=50, min_new_tokens=10):
    """
    Splits long text into chunks, summarizes each, then summarizes all summaries.
    Args:
        text (str): The original text to summarize.
        chunk_size (int): Max characters per chunk.
        max_new_tokens (int): Max tokens for each summary output.
        min_new_tokens (int): Minimum tokens to avoid very short summaries.
    Returns:
        str: Final summarized text.
    """
    # 1. Split text into smaller pieces
    chunks = textwrap.wrap(text, chunk_size)

    # 2. Summarize each chunk separately
    chunk_summaries = []
    for chunk in chunks:
        summary = summarizer(
            chunk,
            max_new_tokens=max_new_tokens,
            min_new_tokens=min_new_tokens,
            do_sample=False,
            truncation=True
        )[0]['summary_text']
        chunk_summaries.append(summary)

    # 3. Combine summaries & summarize again for a neat final summary
    combined_summary = " ".join(chunk_summaries)
    final_summary = summarizer(
        combined_summary,
        max_new_tokens=max_new_tokens,
        min_new_tokens=min_new_tokens,
        do_sample=False,
        truncation=True
    )[0]['summary_text']

    return final_summary

# ---------------- DEMO ----------------
long_text = """
AI is transforming every industry, including healthcare, education, and finance.
In healthcare, AI helps with diagnostics and drug discovery.
In finance, it predicts market trends and improves fraud detection.
In education, AI personalizes learning, automates administrative tasks,
and provides intelligent tutoring systems for students.
These changes are speeding up innovation and improving efficiency worldwide.
"""

# Summarize long text
summary_result = summarize_long_text(long_text, chunk_size=250, max_new_tokens=60, min_new_tokens=20)
print("FINAL SUMMARY:\n", summary_result)
