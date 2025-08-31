import streamlit as st
from elevenlabs.client import ElevenLabs
import fitz 
import tempfile

API_KEY = ""         
VOICE_ID = ""       
MAX_CHARS = 2500                

client = ElevenLabs(api_key=API_KEY)

def extract_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    return "\n".join(page.get_text("text") for page in doc)

def split_text(text):
    words = text.split()
    chunks, current = [], []
    length = 0
    for w in words:
        if length + len(w) + 1 > MAX_CHARS:
            chunks.append(" ".join(current))
            current, length = [], 0
        current.append(w)
        length += len(w) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks

def generate_audiobook(chunks):
    final_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    with open(final_mp3, "wb") as out:
        for i, chunk in enumerate(chunks, start=1):
            st.write(f"Processing chunk {i}/{len(chunks)}...")
            stream = client.text_to_speech.convert(
                voice_id=VOICE_ID,
                model_id="eleven_multilingual_v2",
                text=chunk,
                output_format="mp3_44100_128"
            )
            out.write(b"".join(stream))
    return final_mp3

#UI
st.title("PDF to Audiobook — Cloned Voice")

uploaded = st.file_uploader("Upload PDF", type=["pdf"])
if uploaded and st.button("Generate Audiobook"):
    text = extract_text(uploaded)
    chunks = split_text(text)
    st.write(f"Total chunks: {len(chunks)}")
    mp3_file = generate_audiobook(chunks)
    audio_bytes = open(mp3_file, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")
    st.download_button("Download MP3", audio_bytes, "audiobook.mp3")
