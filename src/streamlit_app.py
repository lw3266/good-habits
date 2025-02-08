import streamlit as st
import sqlite3
import openai
from hashlib import sha256
import random

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
def chat_with_gpt(query):
    client = openai.OpenAI(
    api_key="the openai key"
    )

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
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

    # Initialize messages in session state if they don't exist
    if 'streak_messages' not in st.session_state:
        st.session_state.streak_messages = {}
    
    # Show user stats
    st.write(f"Login Count: {st.session_state['login_count']}")

    # Add tabs for different features
    tab1, tab2 = st.tabs(["Chat with AI", "Habit Tracker"])
    
    with tab1:
        # Chat with ChatGPT
        query = st.text_area("Ask a question to ChatGPT:")
        if st.button("Send"):
            if query:
                response = chat_with_gpt(query)
                st.write(f"ChatGPT: {response}")
            else:
                st.error("Please enter a question.")
    
    with tab2:
        st.subheader("Habit Tracker")
        
        # Form to add new habit
        with st.form("new_habit"):
            st.write("Add New Habit")
            habit_name = st.text_input("Habit Name")
            frequency = st.selectbox("Target Frequency", 
                                   ["Daily", "Weekly", "Monthly"])
            submit = st.form_submit_button("Add Habit")
            
            if submit and habit_name:
                add_habit(st.session_state['username'], habit_name, frequency)
                st.success(f"Added new habit: {habit_name}")
        
        # Display existing habits
        st.write("Your Habits")
        habits = get_user_habits(st.session_state['username'])
        
        if habits:
            for habit in habits:
                # Display any messages for this habit
                habit_key = f"habit_{habit[0]}"
                if habit_key in st.session_state.streak_messages:
                    message, msg_type = st.session_state.streak_messages[habit_key]
                    if msg_type == "success":
                        st.success(message)
                    elif msg_type == "info":
                        st.info(message)
                    elif msg_type == "warning":
                        st.warning(message)
                    # Clear the message after displaying
                    del st.session_state.streak_messages[habit_key]

                col1, col2, col3, col4 = st.columns([2,1,1,1])
                with col1:
                    st.write(f"**{habit[2]}**")  # habit name
                    st.write(f"Frequency: {habit[3]}")  # target frequency
                with col2:
                    st.write(f"Streak: {get_streak_display(habit[6])}")  # streak with fire emojis
                with col3:
                    if st.button("Track", key=f"track_{habit[0]}"):
                        success_message = update_habit_streak(habit[0])
                        habit_key = f"habit_{habit[0]}"
                        if habit[6] % 5 == 4:  # About to hit a milestone
                            st.balloons()
                            st.session_state.streak_messages[habit_key] = (success_message, "success")
                        else:
                            st.session_state.streak_messages[habit_key] = (success_message, "info")
                        st.rerun()
                with col4:
                    if st.button("Reset Streak", key=f"reset_{habit[0]}"):
                        reset_message = reset_habit_streak(habit[0])
                        st.session_state.streak_messages[f"habit_{habit[0]}"] = (reset_message, "warning")
                        st.rerun()
                st.divider()
        else:
            st.info("No habits tracked yet. Add your first habit above!")

# If user is not logged in, show login or register
if 'username' not in st.session_state:
    page = st.selectbox("Select Page", ["Login", "Register"])

    if page == "Login":
        login_page()
    else:
        register_page()
else:
    main_page()
