import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time
from datetime import datetime
import re

load_dotenv()

st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Orbitron:wght@400;700&display=swap');
        body {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #0A0A0A 0%, #1A1A1A 100%);
            color: #FFFFFF;
        }
        h1, h2, h3 { font-family: 'Orbitron', sans-serif; }
        .main-header {
            position: fixed;
            top: 0;
            width: 100%;
            text-align: center;
            padding: 1.5rem;
            background: rgba(0, 0, 0, 0.8);
            border-bottom: 2px solid #00FFFF;
            box-shadow: 0 0 15px #00FFFF;
            animation: slideInLeft 0.5s ease-in;
            z-index: 1000;
        }
        .flag-stripe {
            height: 6px;
            background: linear-gradient(90deg, #FF00FF 33%, #00FFFF 66%, #00FF00 100%);
            animation: slideInLeft 0.5s ease-in;
        }
        .stTextInput > div > input {
            border-radius: 20px;
            padding: 0.8rem 2rem;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00FFFF;
            color: #FFFFFF;
            transition: all 0.3s ease;
        }
        .stTextInput > div > input:focus {
            border-color: #FF00FF;
            box-shadow: 0 0 15px #FF00FF;
        }
        .stButton > button {
            border-radius: 20px;
            padding: 0.6rem 1.5rem;
            background: linear-gradient(135deg, #00FFFF, #FF00FF);
            color: #000000;
            border: none;
            font-weight: bold;
            text-transform: uppercase;
            box-shadow: 0 0 10px #00FFFF;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 20px #FF00FF;
        }
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 255, 0.3);
            padding: 1.5rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 20px #FF00FF;
        }
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background: rgba(0, 0, 0, 0.9);
            padding: 1rem;
            text-align: center;
            border-top: 2px solid #00FFFF;
            animation: fadeIn 0.5s ease-in;
        }
        .sidebar-content {
            padding: 1rem;
            background: rgba(0, 0, 0, 0.9);
            border-right: 2px solid #00FFFF;
            animation: slideInLeft 0.5s ease-in;
        }
        .sidebar-content .stButton > button {
            width: 100%;
            margin-bottom: 1rem;
        }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideInLeft { from { transform: translateX(-100%); } to { transform: translateX(0); } }
    </style>
    """, unsafe_allow_html=True)

local_css()

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are Kanoon ki Pehchaan, an AI assistant specialized in Indian law."}
        ]
    if "response_time" not in st.session_state:
        st.session_state.response_time = 0
    if "chat_started" not in st.session_state:
        st.session_state.chat_started = False

@st.cache_resource
def get_model():
    try:
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
    except Exception as e:
        st.error(f"Failed to initialize model: {e}")
        return None

def is_indian_law_related(query):
    if not query or not isinstance(query, str):
        return False
    query = query.lower()
    indian_legal_keywords = ["indian", "india", "ipc", "crpc", "constitution", "section", "act", "law"]
    for keyword in indian_legal_keywords:
        if keyword in query:
            return True
    patterns = [r"section \d+", r"article \d+", r"ipc \d+"]
    for pattern in patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False

def create_header():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
    st.title("⚖ Kanoon ki Pehchaan")
    st.caption("Your AI-powered Guide to Indian Legal System")
    st.markdown('</div>', unsafe_allow_html=True)

def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(f"""
                <div style="background: rgba(227, 242, 253, 0.2); padding: 12px; border-radius: 15px; border: 1px solid rgba(187, 222, 251, 0.3); margin-bottom: 8px; color: #ffffff;">
                    {message["content"]}
                </div>
                <div style="font-size: 0.8em; color: #bbdefb; text-align: right; margin-top: 4px;">
                    {datetime.now().strftime("%H:%M")}
                </div>
                """, unsafe_allow_html=True)
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="⚖"):
                st.markdown(f"""
                <div style="background: rgba(248, 249, 250, 0.2); padding: 12px; border-radius: 15px; border: 1px solid rgba(233, 236, 239, 0.3); margin-bottom: 8px; color: #ffffff;">
                    {message["content"]}
                </div>
                <div style="font-size: 0.8em; color: #e9ecef; text-align: right; margin-top: 4px;">
                    {datetime.now().strftime("%H:%M")} | ⏱ {st.session_state.response_time:.1f}s
                </div>
                """, unsafe_allow_html=True)

def process_user_input(user_input):
    if not user_input or not user_input.strip():
        return
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"""
        <div style="background: rgba(227, 242, 253, 0.2); padding: 12px; border-radius: 15px; border: 1px solid rgba(187, 222, 251, 0.3); margin-bottom: 8px; color: #ffffff;">
            {user_input}
        </div>
        <div style="font-size: 0.8em; color: #bbdefb; text-align: right; margin-top: 4px;">
            {datetime.now().strftime("%H:%M")}
        </div>
        """, unsafe_allow_html=True)
    is_legal_query = is_indian_law_related(user_input)
    with st.chat_message("assistant", avatar="⚖"):
        if not is_legal_query:
            response = "I can only answer questions related to Indian law."
            st.markdown(f"""
            <div style="background: rgba(248, 249, 250, 0.2); padding: 12px; border-radius: 15px; border: 1px solid rgba(233, 236, 239, 0.3); margin-bottom: 8px; color: #ffffff;">
                {response}
            </div>
            <div style="font-size: 0.8em; color: #e9ecef; text-align: right; margin-top: 4px;">
                {datetime.now().strftime("%H:%M")} | ⏱ 0.0s
            </div>
            """, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            langchain_messages = [SystemMessage(content=m["content"]) if m["role"] == "system" else HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]) for m in st.session_state.messages]
            model = get_model()
            if model:
                start_time = time.time()
                with st.spinner("Researching Indian law..."):
                    enhanced_prompt = f"{langchain_messages[-1].content} Provide information in the context of Indian law."
                    langchain_messages[-1] = HumanMessage(content=enhanced_prompt)
                    result = model.invoke(langchain_messages)
                    end_time = time.time()
                    st.session_state.response_time = end_time - start_time
                    st.markdown(f"""
                    <div style="background: rgba(248, 249, 250, 0.2); padding: 12px; border-radius: 15px; border: 1px solid rgba(233, 236, 239, 0.3); margin-bottom: 8px; color: #ffffff;">
                        {result.content}
                    </div>
                    <div style="font-size: 0.8em; color: #e9ecef; text-align: right; margin-top: 4px;">
                        {datetime.now().strftime("%H:%M")} | ⏱ {st.session_state.response_time:.1f}s
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": result.content})

def main():
    init_session_state()
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.switch_page("account.py")
        return
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("account.py")
        st.markdown("""
        ### About Kanoon ki Pehchaan
        *Kanoon ki Pehchaan* is an AI-powered legal assistant for Indian law.
        ### Key Features
        - Real-time legal assistance
        - Comprehensive Indian law database
        ### Disclaimer
        For informational purposes only. Consult a legal professional for advice.
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    create_header()
    if not st.session_state.chat_started:
        st.info("🙏 Namaste! Welcome to Kanoon ki Pehchaan!")
        st.session_state.chat_started = True
    display_messages()
    user_input = st.chat_input("Ask about Indian laws...")
    if user_input:
        process_user_input(user_input)
    st.markdown('<div class="footer">Powered by Gemini 1.5 Pro</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()