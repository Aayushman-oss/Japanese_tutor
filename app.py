import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

st.set_page_config(page_title="Sensei AI - Japanese Tutor", page_icon="🍡", layout="wide")

st.markdown("""
    <style>
    .big-kanji { font-size: 5rem; text-align: center; color: #E63946; margin-bottom: 0px;}
    .reading { font-size: 1.5rem; text-align: center; color: #457B9D; }
    .meaning { font-size: 1.2rem; text-align: center; font-style: italic; color: #1D3557; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Enter your Google Gemini API Key to start.")
    # Keeping the sidebar input is the SAFEST way to do this in Colab 
    # so your key isn't saved in the notebook history!
    api_key = st.text_input("API Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Key loaded!")
    else:
        st.warning("Please enter your API Key to use the tutor.")
        st.stop()
    
    st.divider()
    st.write("### Tutor Persona")
    tutor_level = st.selectbox("Your Japanese Level", ["Beginner (JLPT N5)", "Intermediate (JLPT N4-N3)", "Advanced (JLPT N2-N1)"])

def get_gemini_response(prompt, system_instruction=None):
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_instruction)
    return model.generate_content(prompt).text

def text_to_speech(text, lang='ja'):
    tts = gTTS(text=text, lang=lang)
    fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    tts.save(temp_path)
    return temp_path

st.title("🍡 Sensei AI: Your Interactive Japanese Tutor")

tab1, tab2 = st.tabs(["🗣️ Chat Practice", "📚 Vocab Builder"])
