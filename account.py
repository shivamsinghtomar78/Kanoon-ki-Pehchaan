import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json
import requests

# Initialize Firebase only if it hasn't been initialized already
if not firebase_admin._apps:
    cred = credentials.Certificate("kanoon-ki-pehchaan-6ff0ed4a9c13.json")
    firebase_admin.initialize_app(cred)

# Custom CSS for Kanoon ki Pehchaan
def local_css():
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
            padding-bottom: 100px;
            color: #ffffff;
        }

        /* Header styling */
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
            backdrop-filter: blur(10px);
            animation: fadeIn 1s ease-in-out;
        }

        .flag-stripe {
            height: 8px;
            background: linear-gradient(90deg, #ff9933 33%, white 33% 66%, #138808 66%);
            margin-bottom: 1rem;
            animation: slideIn 1s ease-in-out;
        }

        /* Input styling */
        .stTextInput input {
            border-radius: 25px !important;
            padding: 1rem !important;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ffffff;
            width: 100%;  /* Full width */
            transition: all 0.3s ease;
        }

        .stTextInput input:focus {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
        }

        /* Button styling */
        .stButton button {
            border-radius: 25px !important;
            padding: 0.5rem 1rem !important;
            background: linear-gradient(135deg, #ff9933 0%, #138808 100%);
            color: #ffffff;
            border: none;
            transition: all 0.3s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        }
    </style>
    """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Kanoon ki Pehchaan",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)
local_css()

# Firebase Authentication functions
def sign_up_with_email_and_password(email, password, username=None):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        st.success('Account created successfully!')
        st.session_state.username = username
        st.session_state.useremail = email
        st.session_state.signedout = True
        st.session_state.signout = True
    except Exception as e:
        st.error(f'Signup failed: {e}')

def sign_in_with_email_and_password(email, password):
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        payload = json.dumps(payload)
        r = requests.post(rest_api_url, params={"key": ""}, data=payload)
        data = r.json()
        if 'email' in data:
            st.session_state.username = data.get('displayName', 'User')
            st.session_state.useremail = data['email']
            st.session_state.signedout = True
            st.session_state.signout = True
        else:
            st.error(data.get('error', {}).get('message', 'Login failed'))
    except Exception as e:
        st.error(f'Signin failed: {e}')

def reset_password(email):
    try:
        rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = {
            "email": email,
            "requestType": "PASSWORD_RESET"
        }
        payload = json.dumps(payload)
        r = requests.post(rest_api_url, params={"key": ""}, data=payload)
        if r.status_code == 200:
            return True, "Reset email Sent"
        else:
            error_message = r.json().get('error', {}).get('message')
            return False, error_message
    except Exception as e:
        return False, str(e)

# Forget Password Function
def forget():
    email = st.text_input('Email')
    if st.button('Send Reset Link'):
        success, message = reset_password(email)
        if success:
            st.success("Password reset email sent successfully.")
        else:
            st.warning(f"Password reset failed: {message}")

# Authentication Page
def auth_page():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.markdown('<div class="flag-stripe"></div>', unsafe_allow_html=True)
    st.title("⚖️ Kanoon ki Pehchaan")
    st.caption("Your AI-powered Guide to Indian Legal System")
    st.markdown('</div>', unsafe_allow_html=True)

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''

    if not st.session_state.get("signedout", False):
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')
        st.session_state.email_input = email
        st.session_state.password_input = password

        if choice == 'Sign up':
            username = st.text_input("Enter your unique username")
            if st.button('Create my account'):
                sign_up_with_email_and_password(email=email, password=password, username=username)
        else:
            st.button('Login', on_click=lambda: sign_in_with_email_and_password(st.session_state.email_input, st.session_state.password_input))
            forget()

# Main Page
def main_page():
    st.title("Welcome to Kanoon ki Pehchaan")
    st.write(f"Hello, {st.session_state.username}!")
    st.write("This is the main page of the application.")

    if st.button('Sign out'):
        st.session_state.clear()
        st.experimental_rerun()

# Run the app
def app():
    if not st.session_state.get("signedout", False):
        auth_page()
    else:
        main_page()

if __name__ == "__main__":
    app()