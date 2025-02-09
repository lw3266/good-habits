import streamlit as st
import openai
from hashlib import sha256
import json
from profile_page import profile_page
from database import (
    create_user_table, 
    store_user, 
    get_user, 
    update_user_stats
)

# Load API key from a JSON file
def load_api_key(filename="config.json"):
    with open(filename, "r") as file:
        data = json.load(file)
        if not data:
            raise ValueError("API key not found in JSON file.")
        return data.get("OPENAI_API_KEY", "").strip()

# Function to interact with ChatGPT
def chat_with_gpt(query):
    client = openai.OpenAI(
        api_key=load_api_key()
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "user", "content": query}
        ]
    )

    return completion.choices[0].message.content

# Streamlit UI
st.title("ChatGPT with User Login and Stats")

# Ensure the user table is created when the app starts
create_user_table()

# Registration Page
def register_page():
    st.subheader("Register New Account")
    
    # Inputs for registration
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type='password')
    
    if st.button('Register'):
        # Check if username already exists
        if get_user(username):
            st.error("Username already exists. Please try a different one.")
        else:
            # Store the user (hashed password)
            hashed_password = sha256(password.encode()).hexdigest()
            store_user(username, hashed_password)
            st.success("Registration successful! Please login to continue.")

# Login Page
def login_page():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button('Login'):
        user = get_user(username)
        if user and sha256(password.encode()).hexdigest() == user[1]:
            st.session_state['username'] = username
            update_user_stats(username)
            # Store all user data in session state
            st.session_state['login_count'] = user[2]
            st.session_state['display_name'] = user[3]
            st.session_state['bio'] = user[4]
            st.success("Login successful!")
            main_page()
        else:
            st.error("Invalid username or password.")

# Main page after login
def main_page():
    st.subheader(f"Welcome {st.session_state['username']}!")
    
    # Inject a hidden HTML element so that the browser extension can obtain the current username.
    st.markdown(
        f"<div id='user-info' style='display: none;'>{st.session_state['username']}</div>",
        unsafe_allow_html=True
    )
    
    # Show user stats
    st.write(f"Login Count: {st.session_state['login_count']}")
    
    # Add a button to navigate to profile page
    if st.button("View Profile"):
        st.session_state['page'] = 'profile'
        st.rerun()
    
    # Chat with ChatGPT
    query = st.text_area("Ask a question to ChatGPT:")
    if st.button("Send"):
        if query:
            response = chat_with_gpt(query)
            st.write(f"ChatGPT: {response}")
        else:
            st.error("Please enter a question.")

# If user is not logged in, show login or register
if 'username' not in st.session_state:
    page = st.selectbox("Select Page", ["Login", "Register"])

    if page == "Login":
        login_page()
    else:
        register_page()
else:
    # Check which page to display
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'
    
    if st.session_state['page'] == 'main':
        main_page()
    elif st.session_state['page'] == 'profile':
        profile_page()

    # Handle force rerun if needed
    if 'force_rerun' in st.session_state and st.session_state['force_rerun']:
        del st.session_state['force_rerun']
        st.rerun()
