import streamlit as st
import sqlite3
import openai
from hashlib import sha256

# Set up OpenAI API Key
openai.api_key = 'key'

# Function to create/connect to the database
def create_connection():
    conn = sqlite3.connect('user_data.db')
    return conn

# Function to create user table (if not exists)
def create_user_table():
    conn = create_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, 
                    password TEXT, 
                    login_count INTEGER)''')
    conn.commit()
    conn.close()

# Function to store new user data
def store_user(username, password):
    conn = create_connection()
    conn.execute('INSERT INTO users (username, password, login_count) VALUES (?, ?, ?)', 
                 (username, password, 0))
    conn.commit()
    conn.close()

# Function to get user by username
def get_user(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to update user stats (e.g., login_count)
def update_user_stats(username):
    conn = create_connection()
    conn.execute('UPDATE users SET login_count = login_count + 1 WHERE username=?', (username,))
    conn.commit()
    conn.close()

# Function to interact with ChatGPT
def chat_with_gpt(query):
    client = openai.OpenAI(
    api_key="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"
    )

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
        {"role": "user", "content": query}
    ]
    )

    return(completion.choices[0].message)

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
            st.session_state['login_count'] = user[2] + 1
            st.success("Login successful!")
            main_page()
        else:
            st.error("Invalid username or password.")

# Main page after login
def main_page():
    st.subheader(f"Welcome {st.session_state['username']}!")

    # Show user stats
    st.write(f"Login Count: {st.session_state['login_count']}")

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
    main_page()
