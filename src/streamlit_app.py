import streamlit as st
import sqlite3
import openai
from hashlib import sha256
import random
import json

# Load API key from a JSON file
def load_api_key(filename="config.json"):
    with open(filename, "r") as file:
        data = json.load(file)
        # Check if key is loaded
        if not data:
            raise ValueError("API key not found in JSON file.")
        
        print("API key loaded successfully.")
        return data.get("OPENAI_API_KEY", "").strip()
    
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
    conn.execute('''CREATE TABLE IF NOT EXISTS habits
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    habit_name TEXT,
                    target_frequency TEXT,
                    created_date DATE,
                    last_tracked DATE,
                    streak INTEGER,
                    FOREIGN KEY (username) REFERENCES users(username))''')
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
def get_habit_context(username):
    habits = get_user_habits(username)
    if not habits:
        return "You haven't started tracking any habits yet."
    
    context = []
    for habit in habits:
        name = habit[2]
        frequency = habit[3]
        streak = habit[6]
        last_tracked = habit[5]
        
        status = f"You're maintaining a {streak}-day streak for {name} ({frequency})"
        if streak == 0 and last_tracked:
            status = f"You recently reset your streak for {name} ({frequency}). Time for a fresh start!"
        elif streak == 0:
            status = f"You've set up {name} ({frequency}) as a new habit to build"
            
        context.append(status)
    
    return "\n".join(context)

def chat_with_gpt(query, username):
    habit_context = get_habit_context(username)
    
    system_prompt = f"""You are a supportive AI assistant who helps users build better habits and plan their days. 
    Here's the user's current habit status:
    {habit_context}
    
    Keep this context in mind when responding. If relevant to their question, provide specific advice about:
    - How to maintain their current streaks
    - How to rebuild after broken streaks
    - How to plan their day around their habits
    - How to stay motivated
    
    Be encouraging but realistic. Acknowledge their progress and setbacks naturally in conversation."""

    client = openai.OpenAI(
        api_key=load_api_key()
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )

    return completion.choices[0].message.content

# Functions for habit tracking
def add_habit(username, habit_name, target_frequency):
    conn = create_connection()
    conn.execute('''INSERT INTO habits 
                    (username, habit_name, target_frequency, created_date, streak) 
                    VALUES (?, ?, ?, DATE('now'), 0)''', 
                    (username, habit_name, target_frequency))
    conn.commit()
    conn.close()

def get_user_habits(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits WHERE username=?', (username,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def get_streak_increment_message(streak):
    # Special milestone messages (when fire emoji is added)
    if streak % 5 == 0:
        milestone_messages = [
            f"🎉 INCREDIBLE! {streak} DAYS! You've earned another 🔥! Your dedication is absolutely inspiring!",
            f"🌟 PHENOMENAL! {streak} days and another 🔥 added to your collection! You're becoming unstoppable!",
            f"⭐ LEGENDARY STATUS! {streak} days and a new 🔥! You're what consistency looks like!",
            f"🏆 BOOM! {streak} days and you've unlocked another 🔥! You're building an empire of good habits!",
            f"🎯 MAGNIFICENT! {streak} days strong! Another 🔥 to show for your incredible journey!"
        ]
        return random.choice(milestone_messages)
    
    # Regular encouragement messages
    regular_messages = [
        "Keep that momentum going! 💪",
        "Another day stronger! 🌱",
        "You're on fire! 🎯",
        "Building that habit like a pro! ⚡",
        "Consistency is your superpower! ✨",
        "Look at you go! 🚀",
        "That's the way! 🌟",
        "Crushing it! 💫",
        "You're on a roll! 🎲",
        "Every day counts! 🎯"
    ]
    return random.choice(regular_messages)

def update_habit_streak(habit_id):
    conn = create_connection()
    cursor = conn.cursor()
    
    # Get current streak before updating
    cursor.execute('SELECT streak FROM habits WHERE id=?', (habit_id,))
    current_streak = cursor.fetchone()[0]
    
    # Update streak
    conn.execute('''UPDATE habits 
                    SET streak = streak + 1,
                        last_tracked = DATE('now')
                    WHERE id=?''', (habit_id,))
    conn.commit()
    conn.close()
    
    # Return appropriate message based on new streak
    return get_streak_increment_message(current_streak + 1)

def get_reset_message():
    messages = [
        "Oof! 😅 Everyone stumbles sometimes. The real champions are the ones who get back up! Want to show that habit who's boss?",
        "Plot twist: This isn't a failure, it's just a dramatic pause in your success story. Ready to start the next chapter? 💪",
        "Well, well, well... look who's hitting the reset button! Remember: The only real L is giving up completely. Let's get back to it! 🚀",
        "Did you just... 😱 No worries! Even Olympic athletes have off days. Tomorrow's a new day to crush it!",
        "Breaking news: Streak broken! But here's the thing - progress isn't perfect. It's messy, it's real, and it starts again NOW! 🌟"
    ]
    tips = [
        "Pro tip: Start small tomorrow. Even tiny wins count!",
        "Quick tip: Set a daily reminder - your future self will thank you.",
        "Hint: Tell a friend about your habit - accountability works wonders!",
        "Suggestion: Put your habit trigger (like running shoes) somewhere visible tonight.",
        "Strategy: Pair this habit with something you already do daily!"
    ]
    return f"{random.choice(messages)}\n\n{random.choice(tips)}"

def reset_habit_streak(habit_id):
    conn = create_connection()
    conn.execute('UPDATE habits SET streak = 0 WHERE id=?', (habit_id,))
    conn.commit()
    conn.close()
    return get_reset_message()

def get_streak_display(streak):
    fire_emojis = '🔥' * (streak // 5)  # Add a fire emoji for every 5 streak points
    return f"{streak} {fire_emojis}"

# Streamlit UI
st.title("Habit Trainer")

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
    # Add hidden element with the username for the extension to detect
    st.markdown(f'<div id="user-info" style="display:none;">{st.session_state["username"]}</div>', unsafe_allow_html=True)

    # Initialize messages in session state if they don't exist
    if 'streak_messages' not in st.session_state:
        st.session_state['streak_messages'] = {}

    # Remove the default padding
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 0rem;
            }
            .stButton button {
                width: 100%;
                padding: 0rem 1rem;
                line-height: 1.6;
            }
            .habit-container {
                background-color: #f0f2f6;
                border-radius: 0.5rem;
                padding: 0.5rem;
                margin-bottom: 0.5rem;
            }
            .main-header {
                color: #0f52ba;
                margin-bottom: 1rem;
            }
            .stat-box {
                padding: 0.5rem;
                border-radius: 0.3rem;
                margin-bottom: 1rem;
            }
            .progress-segment {
                display: inline-block;
                width: 19%;
                height: 4px;
                margin: 0 0.5%;
                background-color: #e0e0e0;
                border-radius: 2px;
            }
            .progress-segment.active {
                background-color: #00c853;
            }
            .chat-container {
                display: flex;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            .chat-input {
                flex: 1;
            }
            .chat-response {
                flex: 1;
                max-height: 300px;
                overflow-y: auto;
                padding: 1rem;
                background-color: #f8f9fa;
                border-radius: 0.5rem;
            }
            .habit-row {
                display: flex;
                flex-direction: column;
                padding: 0.8rem;
                margin: 0.5rem 0;
                background-color: #2c3e50;
                border-radius: 0.5rem;
                border-left: 4px solid #3498db;
            }
            .habit-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 0.5rem;
            }
            .habit-name {
                font-size: 1.1rem;
                font-weight: 600;
                color: #ecf0f1;
                margin-bottom: 0.2rem;
            }
            .habit-details {
                color: #bdc3c7;
                font-size: 0.9rem;
            }
            .streak-display {
                color: #ecf0f1;
                font-weight: 500;
                margin-bottom: 0.5rem;
            }
            .fire-emoji {
                color: #e67e22;
            }
            .habit-controls {
                display: flex;
                gap: 0.5rem;
            }
            .progress-bar {
                margin-bottom: 0.5rem;
            }
            .progress-segment {
                display: inline-block;
                width: 19%;
                height: 3px;
                margin: 0 0.5%;
                background-color: #34495e;
                border-radius: 2px;
            }
            .progress-segment.active {
                background-color: #2ecc71;
            }
            .stButton button {
                background-color: #34495e !important;
                color: #ecf0f1 !important;
                border: none !important;
                padding: 0.3rem !important;
                min-width: 80px !important;
                height: 40px !important;
                border-radius: 4px !important;
                cursor: pointer !important;
                font-size: 1rem !important;
                transition: background-color 0.2s !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                white-space: nowrap !important;
            }
            .stButton button:hover {
                background-color: #3498db !important;
            }
            .habit-row {
                margin-bottom: 0.2rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h2 class='main-header'>Welcome {st.session_state['username']}!</h2>", unsafe_allow_html=True)

    # Show user stats in a nice box
    st.markdown(f"<div class='stat-box'>🔄 Login Count: {st.session_state['login_count']}</div>", unsafe_allow_html=True)

    # Chat section
    st.subheader("💬 Chat with AI")
    
    # Create a container for chat input and response side by side
    chat_cols = st.columns([1, 1])
    
    with chat_cols[0]:
        query = st.text_area("Ask me anything about your habits or daily planning:", height=200)
        if st.button("Send 📤", use_container_width=True):
            if query:
                response = chat_with_gpt(query, st.session_state['username'])
                st.session_state['current_response'] = response
            else:
                st.error("Please enter a question.")
    
    with chat_cols[1]:
        if 'current_response' in st.session_state:
            st.markdown(f"""
                <div style="height: 300px; overflow-y: auto; padding: 1rem; 
                    background-color: #2c3e50; border-radius: 0.5rem; color: #ecf0f1;">
                    {st.session_state['current_response']}
                </div>
            """, unsafe_allow_html=True)

    # Habit section
    st.subheader("📊 Habit Tracker")
    
    # Form to add new habit
    with st.form("new_habit", clear_on_submit=True):
        cols = st.columns([3, 2, 1])
        with cols[0]:
            habit_name = st.text_input("Name")
        with cols[1]:
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
        with cols[2]:
            submit = st.form_submit_button("Add Habit", use_container_width=True)
        
        if submit and habit_name:
            add_habit(st.session_state['username'], habit_name, frequency)
            st.success(f"Added new habit: {habit_name}")
    
    # Display existing habits
    habits = get_user_habits(st.session_state['username'])
    
    if habits:
        for habit in habits:
            habit_key = f"habit_{habit[0]}"
            if habit_key in st.session_state.streak_messages:
                message, msg_type = st.session_state.streak_messages[habit_key]
                if msg_type == "success":
                    st.success(message)
                elif msg_type == "info":
                    st.info(message)
                elif msg_type == "warning":
                    st.warning(message)
                del st.session_state.streak_messages[habit_key]

            # Progress bar
            progress_html = ""
            current_progress = habit[6] % 5
            for i in range(5):
                if i < current_progress:
                    progress_html += "<div class='progress-segment active'></div>"
                else:
                    progress_html += "<div class='progress-segment'></div>"
            
            # Create the buttons vertically
            col1, col2 = st.columns([1, 7])
            with col1:
                button1 = st.button("Done!", key=f"track_{habit[0]}", help="Increment streak")
                button2 = st.button("↺", key=f"reset_{habit[0]}", help="Reset streak")
            
            # Then show the habit display
            with col2:
                st.markdown(f"""
                    <div class='habit-row'>
                        <div class='progress-bar'>
                            {progress_html}
                        </div>
                        <div style="display: flex; align-items: center;">
                            <div>
                                <div class="habit-name">{habit[2]}</div>
                                <div class="habit-details">{habit[3]}</div>
                                <div class="streak-display">
                                    Streak: <span class="fire-emoji">{get_streak_display(habit[6])}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if button1:
                success_message = update_habit_streak(habit[0])
                if habit[6] % 5 == 4:
                    st.balloons()
                    st.session_state.streak_messages[habit_key] = (success_message, "success")
                else:
                    st.session_state.streak_messages[habit_key] = (success_message, "info")
                st.rerun()
            if button2:
                reset_message = reset_habit_streak(habit[0])
                st.session_state.streak_messages[habit_key] = (reset_message, "warning")
                st.rerun()
    else:
        st.info("No habits tracked yet. Add your first habit above! 🎯")

# If user is not logged in, show login or register
if 'username' not in st.session_state:
    page = st.selectbox("Select Page", ["Login", "Register"])

    if page == "Login":
        login_page()
    else:
        register_page()
else:
    main_page()
