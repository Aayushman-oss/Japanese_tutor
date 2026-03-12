import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import tempfile

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sensei AI - Japanese Tutor", page_icon="🍡", layout="wide")

# --- CUSTOM CSS FOR VISUALS ---
st.markdown("""
    <style>
    .big-kanji { font-size: 5rem; text-align: center; color: #E63946; margin-bottom: 0px;}
    .reading { font-size: 1.5rem; text-align: center; color: #457B9D; }
    .meaning { font-size: 1.2rem; text-align: center; font-style: italic; color: #1D3557; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR & API KEY ---
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("### Tutor Persona")
    tutor_level = st.selectbox("Your Japanese Level", ["Beginner (JLPT N5)", "Intermediate (JLPT N4-N3)", "Advanced (JLPT N2-N1)"])
    
    st.divider()
    
    st.write("Enter your Google Gemini API Key to start.")
    api_key = st.text_input("API Key", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API Key loaded!")
    else:
        st.warning("Please enter your API Key to use the tutor.")
        st.stop() # Stops the rest of the app from loading until the key is entered

# --- HELPER FUNCTIONS ---
def get_gemini_response(prompt, system_instruction=None):
    """Fetches response from Gemini."""
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction
    )
    response = model.generate_content(prompt)
    return response.text

def text_to_speech(text, lang='ja'):
    """Converts Japanese text to audio and returns the file path."""
    tts = gTTS(text=text, lang=lang)
    fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    tts.save(temp_path)
    return temp_path

# --- MAIN APP UI ---
st.title("🍡 Sensei AI: Your Interactive Japanese Tutor")
st.write("Welcome! Practice your conversation skills or learn new vocabulary.")

# Create tabs for different learning modes
tab1, tab2 = st.tabs(["🗣️ Chat Practice", "📚 Vocab Builder"])

# === TAB 1: CHAT PRACTICE ===
with tab1:
    st.header("Chat with Sensei")
    st.write(f"Currently adjusting to: **{tutor_level}** level.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Say something in Japanese (or ask a grammar question)..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # System prompt for the tutor
        system_prompt = f"""You are an encouraging Japanese language tutor. The student is at a {tutor_level} level. 
        If they speak Japanese, reply in Japanese (with romaji and English translation in brackets). 
        If they make a grammar mistake, gently correct them. 
        If they ask a question in English, explain the Japanese concept clearly."""

        # Fetch AI response (passing the recent conversation for context)
        conversation_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        
        with st.spinner("Sensei is typing..."):
            try:
                reply = get_gemini_response(conversation_context, system_instruction=system_prompt)
                # Display assistant response
                with st.chat_message("assistant"):
                    st.markdown(reply)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error communicating with API: {e}")

# === TAB 2: VOCAB BUILDER ===
with tab2:
    st.header("Dynamic Vocab Builder")
    st.write("Click the button to generate a random Japanese word suited for your level!")
    
    if st.button("🎲 Generate New Word", use_container_width=True):
        with st.spinner("Finding a good word..."):
            vocab_prompt = f"""Give me one random Japanese word appropriate for a {tutor_level} student.
            Format EXACTLY like this with the pipe symbol:
            Kanji|Hiragana/Katakana|Romaji|English Meaning|Example sentence in Japanese|Example sentence English translation"""
            
            try:
                response = get_gemini_response(vocab_prompt)
                parts = response.strip().split('|')
                
                if len(parts) >= 6:
                    kanji, kana, romaji, meaning, ex_ja, ex_en = parts[:6]
                    
                    # Display visually using custom CSS
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<div class='big-kanji'>{kanji}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='reading'>{kana} ({romaji})</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='meaning'>\"{meaning}\"</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    st.write("**Example:**")
                    st.info(f"{ex_ja}\n\n*{ex_en}*")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Generate and play audio
                    audio_file = text_to_speech(ex_ja)
                    st.write("🔊 Listen to the example:")
                    st.audio(audio_file, format='audio/mp3')
                    
                else:
                    st.error("The API returned an unexpected format. Please try again.")
            except Exception as e:
                st.error(f"Error: {e}")
