
'''
pip install "numpy<2" openai openai-whisper streamlit transformers fpdf

And if you're on Mac, you also need:
brew install ffmpeg


'''
import os
import io
import math
import glob
import subprocess
import tempfile
from typing import List

import streamlit as st
from fpdf import FPDF
from openai import OpenAI

# ================== API KEY HANDLING ==================
def get_api_key(name: str = "OPENAI_API_KEY") -> str | None:
    # Prefer ENV
    v = os.getenv(name)
    if v:
        return v
    # Then Streamlit secrets
    try:
        return st.secrets[name]
    except Exception:
        return None

OPENAI_API_KEY = get_api_key()
if not OPENAI_API_KEY:
    st.warning("No API key found in env or Streamlit secrets. Enter it for this session:")
    OPENAI_API_KEY = st.text_input("OpenAI API Key", type="password", help="This is not saved.")
    if not OPENAI_API_KEY:
        st.stop()

client = OpenAI(api_key=OPENAI_API_KEY)

# ================== UI ==================
st.set_page_config(page_title="VidMeet Minutes", layout="centered")
st.title("🎥 VidMeet Minutes: AI-Powered Meeting Summarizer")

st.subheader("📤 Step 1: Upload Your Meeting Video")
video_input = st.file_uploader("Upload an .mp4 file", type=["mp4"])

use_cloud_transcribe = st.checkbox(
    "Use cloud transcription (OpenAI Whisper API)", value=False,
    help="Enable this if local Whisper model isn't available."
)
st.caption("Note: Cloud transcription has a ~25 MB per-file limit. This app compresses and auto-segments if needed.")

# ================== PATHS ==================
UPLOADED_VIDEO = "meeting_video.mp4"
AUDIO_MP3 = "audio_compressed.mp3"  # small, 16 kHz mono, 32 kbps
TMP_DIR = tempfile.mkdtemp(prefix="vidmeet_")

# ================== HELPERS ==================
def run_cmd(cmd: list[str]) -> None:
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def extract_audio_small_mp3(input_video: str, output_mp3: str) -> None:
    """
    Create a very small MP3 (mono, 16 kHz, 32 kbps) – ideal for Whisper API and still fine for ASR.
    """
    cmd = [
        "ffmpeg", "-y", "-i", input_video,
        "-vn",
        "-ac", "1",          # mono
        "-ar", "16000",      # 16 kHz
        "-b:a", "32k",       # 32 kbps (≈0.24 MB/min)
        "-f", "mp3",
        output_mp3
    ]
    run_cmd(cmd)

def file_size_mb(path: str) -> float:
    return os.path.getsize(path) / (1024 * 1024)

def segment_mp3(input_mp3: str, out_dir: str, minutes: int = 9) -> List[str]:
    """
    Segment audio into ~9-minute chunks to ensure each file < 25MB (32kbps ≈ 0.24 MB/min => ~2.2 MB/9min).
    """
    os.makedirs(out_dir, exist_ok=True)
    pattern = os.path.join(out_dir, "part_%03d.mp3")
    # -segment_time takes seconds
    cmd = [
        "ffmpeg", "-y", "-i", input_mp3,
        "-f", "segment",
        "-segment_time", str(minutes * 60),
        "-reset_timestamps", "1",
        pattern
    ]
    run_cmd(cmd)
    parts = sorted(glob.glob(os.path.join(out_dir, "part_*.mp3")))
    return parts

def transcribe_local_whisper(paths: List[str]) -> str:
    import whisper
    # Use tiny to avoid big downloads; switch to "small" if you have space/certs working
    model = whisper.load_model("tiny")
    texts = []
    for p in paths:
        r = model.transcribe(p, language="en")
        texts.append((r.get("text") or "").strip())
    return "\n".join(texts).strip()

def transcribe_cloud_whisper(paths: List[str]) -> str:
    texts = []
    for p in paths:
        if file_size_mb(p) >= 24.9:
            raise RuntimeError(f"Chunk still too large for API (~25MB): {p} is {file_size_mb(p):.2f} MB")
        with open(p, "rb") as f:
            tr = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        texts.append(tr.strip())
    return "\n".join(texts).strip()

def summarize_with_gpt(transcript: str) -> str:
    prompt = (
        "Write a clear, structured executive summary of this meeting "
        "(200–300 words). Use short paragraphs and bullet points for "
        "key topics, decisions, blockers/risks, and next steps.\n\n"
        f"MEETING TRANSCRIPT:\n{transcript}"
    )
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return r.choices[0].message.content.strip()

def actions_with_gpt(transcript: str) -> str:
    prompt = (
        "Extract action items and decisions from the meeting transcript. "
        "Return as bullet points. For each action include Owner (if known), "
        "Task, and Due Date (if mentioned). If missing, use 'Owner: TBD' or 'Due: TBD'.\n\n"
        f"MEETING TRANSCRIPT:\n{transcript}"
    )
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return r.choices[0].message.content.strip()

def save_as_pdf(summary: str, actions: str, filename: str = "meeting_minutes.pdf") -> str:
    def strip_unicode(text: str) -> str:
        return "".join(c for c in text if ord(c) < 256)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, "Meeting Summary")
    pdf.multi_cell(0, 10, strip_unicode(summary))
    pdf.ln()
    pdf.multi_cell(0, 10, "Action Items & Decisions")
    pdf.multi_cell(0, 10, strip_unicode(actions))
    pdf.output(filename)
    return filename

def cleanup(paths: List[str]) -> None:
    for p in paths:
        try:
            if os.path.isdir(p):
                # remove segment files
                for fp in glob.glob(os.path.join(p, "*")):
                    try: os.remove(fp)
                    except: pass
                os.rmdir(p)
            else:
                os.remove(p)
        except Exception:
            pass

# ================== MAIN ==================
if video_input:
    # Preview
    video_bytes = video_input.read()
    st.video(io.BytesIO(video_bytes))
    with open(UPLOADED_VIDEO, "wb") as f:
        f.write(video_bytes)

    # Step 2: extract audio (compact)
    st.subheader("🔊 Step 2: Extracting and compressing audio…")
    try:
        extract_audio_small_mp3(UPLOADED_VIDEO, AUDIO_MP3)
        st.success(f"✅ Audio extracted: {file_size_mb(AUDIO_MP3):.2f} MB")
    except Exception as e:
        st.error(f"FFmpeg failed to extract audio: {e}")
        cleanup([UPLOADED_VIDEO, AUDIO_MP3, TMP_DIR])
        st.stop()

    # Step 3: Transcription (with auto-segmentation if needed)
    st.subheader("📝 Step 3: Transcription")
    transcript = ""
    segment_dir = os.path.join(TMP_DIR, "segments")
    parts = [AUDIO_MP3]

    # If still big for Whisper API, pre-segment to 9-min chunks (also safe for local)
    if use_cloud_transcribe and file_size_mb(AUDIO_MP3) > 24.0:
        st.info("Audio > 24MB. Segmenting into 9-minute chunks for the API limit…")
        parts = segment_mp3(AUDIO_MP3, segment_dir, minutes=9)
        st.caption(f"Created {len(parts)} chunks (each ≪ 25 MB).")

    local_error = None
    if not use_cloud_transcribe:
        try:
            transcript = transcribe_local_whisper(parts)
            st.caption("✅ Local Whisper transcription succeeded.")
        except Exception as e:
            local_error = str(e)
            st.warning("Local Whisper failed. Falling back to OpenAI Whisper API…")
            use_cloud_transcribe = True  # force fallback

    if use_cloud_transcribe and not transcript:
        try:
            transcript = transcribe_cloud_whisper(parts)
            st.caption("✅ Cloud Whisper transcription succeeded.")
        except Exception as e:
            st.error("Transcription failed (local & cloud).")
            if local_error:
                with st.expander("Local Whisper error"):
                    st.code(local_error)
            with st.expander("Cloud Whisper error"):
                st.code(str(e))
            cleanup([UPLOADED_VIDEO, AUDIO_MP3, segment_dir, TMP_DIR])
            st.stop()

    st.text_area("📄 Full Transcript", transcript, height=300)

    # Step 4: Summary
    st.subheader("📌 Step 4: GPT Summary")
    try:
        final_summary = summarize_with_gpt(transcript)
    except Exception as e:
        st.error(f"Summarization failed: {e}")
        cleanup([UPLOADED_VIDEO, AUDIO_MP3, segment_dir, TMP_DIR])
        st.stop()
    st.text_area("📍 Summary", final_summary, height=220)

    # Step 5: Actions
    st.subheader("🧠 Step 5: Action Items & Decisions")
    try:
        action_items = actions_with_gpt(transcript)
    except Exception as e:
        st.error(f"Action extraction failed: {e}")
        cleanup([UPLOADED_VIDEO, AUDIO_MP3, segment_dir, TMP_DIR])
        st.stop()
    st.text_area("📝 Action Items & Decisions", action_items, height=220)

    # Step 6: PDF
    st.subheader("📄 Step 6: Download PDF Summary")
    pdf_file = save_as_pdf(final_summary, action_items)
    with open(pdf_file, "rb") as f:
        st.download_button(
            "⬇️ Download Meeting Minutes (PDF)",
            data=f, file_name=pdf_file, mime="application/pdf"
        )

    st.success("🎉 Meeting minutes generated successfully!")

    # Cleanup best-effort
    cleanup([UPLOADED_VIDEO, AUDIO_MP3, segment_dir, pdf_file, TMP_DIR])
