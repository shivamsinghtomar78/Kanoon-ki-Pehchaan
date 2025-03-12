import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os
import time
import pandas as pd
from datetime import datetime
import base64
import re

# Load environment variables
load_dotenv()

# Page configuration and styling
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
def local_css():
    st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --main-color: #1e3a8a;
            --accent-color: #3b82f6;
            --light-color: #dbeafe;
            --dark-color: #1e293b;
            --background-color: #f8fafc;
            --indian-flag-orange: #FF9933;
            --indian-flag-white: #FFFFFF;
            --indian-flag-green: #138808;
        }
        
        /* Main page styling */
        .main {
            background-color: var(--background-color);
        }
        
        /* Header styling */
        .main-header {
            color: var(--main-color);
            text-align: center;
            font-family: 'Georgia', serif;
            margin-bottom: 30px;
            padding: 20px;
            border-bottom: 2px solid var(--light-color);
        }
        
        /* Indian flag colors for header decoration */
        .flag-stripe {
            height: 6px;
            width: 100%;
            display: flex;
        }
        
        .flag-orange {
            background-color: var(--indian-flag-orange);
            height: 100%;
            width: 33.33%;
        }
        
        .flag-white {
            background-color: var(--indian-flag-white);
            height: 100%;
            width: 33.33%;
        }
        
        .flag-green {
            background-color: var(--indian-flag-green);
            height: 100%;
            width: 33.33%;
        }
        
        /* Chat container */
        .chat-container {
            background-color: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            max-height: 70vh;
            overflow-y: auto;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background-color: var(--main-color);
            color: white;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: var(--accent-color);
            color: white;
            border-radius: 5px;
            border: none;
            padding: 8px 16px;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: var(--main-color);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        /* Chat input styling */
        .stTextInput>div>div>input {
            border-radius: 30px;
            padding: 10px 20px;
            border: 2px solid var(--light-color);
        }
        
        /* Divider */
        hr {
            border-top: 1px solid var(--light-color);
            margin: 20px 0;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: var(--dark-color);
            font-size: 0.8em;
            margin-top: 30px;
        }
        
        /* Message metadata */
        .message-meta {
            font-size: 0.7em;
            opacity: 0.7;
            margin-top: 5px;
            clear: both;
        }
        
        /* Citation styling */
        .citation {
            background-color: #f1f5f9;
            border-left: 3px solid var(--accent-color);
            padding: 10px;
            margin: 10px 0;
            font-size: 0.9em;
        }
        
        /* Loading animation */
        .loading-animation {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
        }
    </style>
    """, unsafe_allow_html=True)

local_css()

# Indian legal categories
indian_legal_categories = [
    "Constitutional Law", "Criminal Law (IPC)", "Civil Law", "Family Law",
    "Property Law", "Contract Law", "Tort Law", "Corporate Law",
    "Intellectual Property", "Tax Law", "Labor Law", "Environmental Law",
    "Consumer Protection", "Cyber Law", "Banking Law", "Insurance Law", 
    "Motor Vehicle Act", "Right to Information"
]

# Indian legal keywords for filtering
indian_legal_keywords = [
    "indian", "india", "ipc", "crpc", "constitution", "section", "act", "law", "legal",
    "supreme court", "high court", "district court", "tribunal", "judge", "advocate",
    "petition", "writ", "fir", "case", "bill", "parliament", "legislation",
    "fundamental rights", "directive principles", "preamble", "arrest", "bail",
    "property", "marriage", "divorce", "inheritance", "contract", "company", 
    "gst", "income tax", "consumer", "cyber", "digital", "reservation",
    "pil", "public interest litigation", "article", "amendment", "ibc", "rbi",
    "sebi", "ministry", "police", "criminal", "civil", "procedure", "evidence",
    "negotiable instruments", "arbitration", "lok adalat", "nyaya panchayat",
    "judicial review", "hindu", "muslim", "christian", "parsi", "personal law",
    "lok sabha", "rajya sabha", "ordinance", "notification", "gazette"
]

# Sample FAQ data for Indian law
indian_faq_data = {
    "What is Kanoon ki Pehchaan?": "Kanoon ki Pehchaan is an AI-powered Indian legal assistant designed to help you understand Indian legal concepts and find relevant legal information about Indian laws.",
    "Is this legal advice?": "No, Kanoon ki Pehchaan provides information for educational purposes only. It's not a substitute for professional legal advice from an Indian advocate.",
    "What types of questions can I ask?": "You can ask questions about Indian laws, legal procedures, constitutional provisions, and legal rights in India. Please note that the application is focused only on Indian law.",
    "Is my data secure?": "Your conversations are stored only in your browser session and are cleared when you refresh the page or close the browser."
}

# Function to check if a query is related to Indian law
def is_indian_law_related(query):
    query = query.lower()
    
    # Check for presence of Indian legal keywords
    for keyword in indian_legal_keywords:
        if keyword.lower() in query:
            return True
            
    # Check for specific Indian legal patterns
    patterns = [
        r"section \d+", r"article \d+", r"ipc \d+", r"crpc \d+",
        r"act of \d{4}", r"indian constitution", r"supreme court",
        r"high court", r"lok adalat", r"legal rights in india",
        r"indian penal", r"criminal procedure", r"civil procedure"
    ]
    
    for pattern in patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    
    return False

# Initialize model with caching for speed
@st.cache_resource
def get_model():
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)

model = get_model()

# Function to create the header
def create_header():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"><div class="flag-orange"></div><div class="flag-white"></div><div class="flag-green"></div></div>', unsafe_allow_html=True)
    st.title("Kanoon ki Pehchaan")
    st.subheader("Indian Legal Assistant")
    st.markdown('</div>', unsafe_allow_html=True)

# Function to display chat messages from session state
def display_messages():
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

# Function to save chat history
def save_chat_history():
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        # Convert chat history to DataFrame
        history_data = []
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                history_data.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        if history_data:
            df = pd.DataFrame(history_data)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="indian_law_chat_history.csv">Download Chat History</a>'
            return href
    return ""

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are an Indian legal assistant named Kanoon ki Pehchaan. You ONLY provide information about Indian laws, the Indian Constitution, Indian legal procedures, and the Indian legal system. If asked about laws from other countries or non-legal topics, politely explain that you can only assist with Indian law questions. When providing legal information, include relevant sections of Indian laws, cite Indian legal cases when applicable, and always clarify that this is for informational purposes only and not legal advice. Always structure answers within the Indian legal context."}
    ]

if "response_time" not in st.session_state:
    st.session_state.response_time = 0

if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if "selected_category" not in st.session_state:
    st.session_state.selected_category = None

# Main app layout
create_header()

# Create two columns for main layout
col1, col2 = st.columns([3, 1])

with col1:
    # Welcome message if chat not started
    if not st.session_state.chat_started:
        st.info("🙏 Namaste! Welcome to Kanoon ki Pehchaan! I'm your Indian legal assistant. How can I help you understand Indian laws today?")
        st.session_state.chat_started = True
    
    # Display chat messages using Streamlit's native chat_message component
    display_messages()
    
    # User input area
    user_input = st.chat_input("Ask about Indian laws and legal matters...")
    
    # Process user input
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display the user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Check if query is related to Indian law
        is_legal_query = is_indian_law_related(user_input)
        
        with st.chat_message("assistant"):
            # If not related to Indian law, provide a redirect response
            if not is_legal_query:
                response = "I apologize, but I can only answer questions related to Indian law and the Indian legal system. Please rephrase your question to focus on Indian legal matters. For example, you can ask about Indian Constitutional law, IPC sections, property laws in India, or Indian court procedures."
                st.write(response)
                # Add response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                # Convert messages to LangChain format for the model
                langchain_messages = []
                for message in st.session_state.messages:
                    if message["role"] == "system":
                        langchain_messages.append(SystemMessage(content=message["content"]))
                    elif message["role"] == "user":
                        langchain_messages.append(HumanMessage(content=message["content"]))
                    elif message["role"] == "assistant":
                        langchain_messages.append(AIMessage(content=message["content"]))
                
                # Get AI response with timing
                start_time = time.time()
                
                with st.spinner("Researching Indian law..."):
                    # If a category is selected, add it to the prompt
                    category_prompt = ""
                    if st.session_state.selected_category:
                        category_prompt = f" Focus your response on {st.session_state.selected_category} in the Indian context if relevant."
                    
                    # Enhance the prompt with Indian law focus
                    enhanced_prompt = (
                        f"{langchain_messages[-1].content}{category_prompt} "
                        "Please provide information specifically in the context of Indian law, "
                        "citing relevant sections, provisions, or case laws from India where applicable."
                    )
                    langchain_messages[-1] = HumanMessage(content=enhanced_prompt)
                    
                    result = model.invoke(langchain_messages)
                    end_time = time.time()
                    st.session_state.response_time = end_time - start_time
                    
                    # Display the response
                    st.write(result.content)
                
                # Add AI response to chat history
                st.session_state.messages.append({"role": "assistant", "content": result.content})

# Sidebar with features
with st.sidebar:
    st.image("https://placehold.co/600x400/1e3a8a/white?text=Kanoon+ki+Pehchaan&font=playfair", use_container_width=True)
    
    st.markdown("## Indian Legal Categories")
    selected_category = st.selectbox("Filter by Indian legal domain:", 
                                    ["All Categories"] + indian_legal_categories)
    
    if selected_category != "All Categories":
        st.session_state.selected_category = selected_category
    else:
        st.session_state.selected_category = None
    
    st.markdown("## Popular Indian Legal Acts")
    acts_expander = st.expander("Click to see major Indian acts")
    with acts_expander:
        st.markdown("""
        - Constitution of India
        - Indian Penal Code, 1860
        - Code of Criminal Procedure, 1973
        - Code of Civil Procedure, 1908
        - Indian Contract Act, 1872
        - Transfer of Property Act, 1882
        - Hindu Marriage Act, 1955
        - Muslim Personal Law (Shariat) Application Act, 1937
        - Companies Act, 2013
        - Income Tax Act, 1961
        - Goods and Services Tax Act, 2017
        - Right to Information Act, 2005
        - Consumer Protection Act, 2019
        """)
    
    st.markdown("## Tools")
    
    # Chat history export
    st.markdown("### Export Chat")
    download_link = save_chat_history()
    st.markdown(download_link, unsafe_allow_html=True)
    
    # Response metrics
    if st.session_state.response_time > 0:
        st.markdown("### Response Metrics")
        st.metric("Last Response Time", f"{st.session_state.response_time:.2f}s")
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {"role": "system", "content": "You are an Indian legal assistant named Kanoon ki Pehchaan. You ONLY provide information about Indian laws, the Indian Constitution, Indian legal procedures, and the Indian legal system. If asked about laws from other countries or non-legal topics, politely explain that you can only assist with Indian law questions. When providing legal information, include relevant sections of Indian laws, cite Indian legal cases when applicable, and always clarify that this is for informational purposes only and not legal advice. Always structure answers within the Indian legal context."}
        ]
        st.session_state.chat_started = False
        st.rerun()
    
    # FAQ Accordion
    st.markdown("### Frequently Asked Questions")
    for question, answer in indian_faq_data.items():
        with st.expander(question):
            st.write(answer)
    
    # Disclaimer
    st.markdown("### Disclaimer")
    st.warning(
        "This application provides information about Indian laws for educational purposes only. "
        "It is not a substitute for professional legal advice. "
        "Please consult a qualified Indian advocate for specific legal concerns."
    )
    
    # Footer
    st.markdown("---")
    st.markdown("### About")
    st.info(
        "Kanoon ki Pehchaan is an AI-powered Indian legal assistant designed to help you understand Indian legal concepts and navigate the complexities of the Indian legal system."
    )
    st.markdown("© 2025 Kanoon ki Pehchaan")

# Footer
st.markdown('<div class="footer">Powered by Google Gemini 1.5 Pro | Made in India 🇮🇳</div>', unsafe_allow_html=True)