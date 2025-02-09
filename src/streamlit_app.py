import streamlit as st
import sqlite3
import openai
from hashlib import sha256
import random
import json
from profile_page import profile_page
from database import *

# Load API key from a JSON file
def load_api_key(filename="config.json"):
    with open(filename, "r") as file:
        data = json.load(file)
        # Check if key is loaded
        if not data:
            raise ValueError("API key not found in JSON file.")
        
        print("API key loaded successfully.")
        return data.get("OPENAI_API_KEY", "").strip()

# Load API key from a JSON file
def load_api_key(filename="config.json"):
    with open(filename, "r") as file:
        data = json.load(file)
        if not data:
            raise ValueError("API key not found in JSON file.")
        return data.get("OPENAI_API_KEY", "").strip()

create_user_table()

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
            print(user)
            st.session_state['login_count'] = user[4]  # Correct index for login_count
            st.session_state['display_name'] = user[2]  # Correct index for display_name
            st.session_state['bio'] = user[3]  # Correct index for bio
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
            response = chat_with_gpt(query, st.session_state['username'])
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
