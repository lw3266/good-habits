import streamlit as st
import openai
from hashlib import sha256
import json
import time
from profile_page import profile_page
from database import (
    create_user_table, create_tabs_table, 
    get_user, store_user, update_user_stats, get_tabs, print_all_content, get_tabs
)
from habit_functions import (
    add_habit, get_user_habits,
    get_streak_increment_message, update_habit_streak,
    get_reset_message, reset_habit_streak, get_streak_display
)

# === Helper to load the API key ===
def load_api_key(filename="config.json"):
    with open(filename, "r") as file:
        data = json.load(file)
        if not data:
            raise ValueError("API key not found in JSON file.")
        print("API key loaded successfully.")
        return data.get("OPENAI_API_KEY", "").strip()

# Make sure the necessary tables exist.
create_user_table()
create_tabs_table()

# === Context Functions ===
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
        
        status = f"You're maintaining a {streak}-day streak for {name} ({frequency})."
        if streak == 0 and last_tracked:
            status = f"You recently reset your streak for {name} ({frequency}). Time for a fresh start!"
        elif streak == 0:
            status = f"You've set up {name} ({frequency}) as a new habit to build."
            
        context.append(status)
    
    return "\n".join(context)

def get_tab_stat_context(username):
    tabs = get_tabs(username)
    if not tabs:
        return "No tab data available."
    lines = []
    for tab in tabs:
        title, url, duration, timestamp = tab
        lines.append(f"{title}: open for {duration:.2f} seconds")
    return "\n".join(lines)

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
    
    client = openai.OpenAI(api_key=load_api_key())
    
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    
    return completion.choices[0].message.content

# === Streamlit UI Code ===

st.title("Good Habits")

# Registration Page
def register_page():
    st.subheader("Register New Account")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type='password')
    if st.button('Register'):
        if get_user(username):
            st.error("Username already exists. Please try a different one.")
        else:
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
            st.session_state['login_count'] = user[4]
            st.session_state['display_name'] = user[2]
            st.session_state['bio'] = user[3]
        else:
            st.error("Invalid username or password.")

# Main page after login
# Main page after login
def main_page():
    print_all_content()
    st.markdown(f'<div id="user-info" style="display:none;">{st.session_state["username"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<h2 class='main-header'>Welcome {st.session_state['username']}!</h2>", unsafe_allow_html=True)
    
    st.subheader("Tab Statistics")
    # Retrieve only the tabs for the logged-in user.
    tabs = get_tabs(st.session_state["username"].strip())
    if tabs:
        for tab in tabs:
            title, url, duration, timestamp = tab
            st.write(f"**Title:** {title} | **URL:** {url} | **Duration:** {duration:.2f}s")
    else:
        st.info("No tab data available. The feature for obtaining real time tab information is not fully functional. We will assume the following configuration: one youtube tab playing music video, one google search tab on deepseek, and one gmail tab. Also note that the following generated message is originally intended to be a pop up notification that gets your attention depending on your browser activeness.")
    
    if st.button("Get ChatGPT Analysis of Tab Stats"):
        # tab_context = get_tab_stat_context(st.session_state["username"])
        tab_context = "(159, John, 'My Heart Will Go On', 'https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.youtube.com/watch%3Fv%3DWNIPqafd4As&ved=2ahUKEwi818nP_LaLAxUomokEHWnuEhoQtwJ6BAg4EAI&usg=AOvVaw1phPR1Cyly8Vk9K4HkevSo', 1372.746, 1739114954)(160, John, 'Gmail: Private and secure email at no cost', 'https://workspace.google.com/intl/en-US/gmail/', 1366.068, 1739114954)(161, John, 'deep seek - Google Search', 'https://www.google.com/search?client=firefox-b-1-d&q=deep+seek', 1257.444, 1739114954"
        query = f"Based on my current tab usage stats:\n{tab_context}\nPlease provide some insights or suggestions in one or two sentences that encourages me to keep up with my goal."
        response = chat_with_gpt(query, st.session_state["username"])
        st.session_state['chat_response'] = response  # Store the response in session state
        
        st.success("ChatGPT Analysis has been sent as a notification.")
    
    # Display the ChatGPT response (if available)
    if 'chat_response' in st.session_state:
        st.subheader("ChatGPT Analysis of Tab Stats")
        st.markdown(f"""
            <div style="padding: 1rem; background-color: #2c3e50; border-radius: 0.5rem; color: #ecf0f1;">
                {st.session_state['chat_response']}
            </div>
        """, unsafe_allow_html=True)
    
    st.subheader("💬 Chat with AI")
    chat_cols = st.columns([1, 1])
    with chat_cols[0]:
        query = st.text_area("Ask me anything about your habits or planning:", height=200)
        if st.button("Send 📤", key="send_chat"):
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
    
    st.subheader("📊 Habit Tracker")
    with st.form("new_habit", clear_on_submit=True):
        cols = st.columns([3, 2, 1])
        with cols[0]:
            habit_name = st.text_input("Name")
        with cols[1]:
            frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
        with cols[2]:
            submit = st.form_submit_button("Add Habit")
        if submit and habit_name:
            add_habit(st.session_state['username'], habit_name, frequency)
            st.success(f"Added new habit: {habit_name}")
    habits = get_user_habits(st.session_state['username'])
    if habits:
        for habit in habits:
            habit_key = f"habit_{habit[0]}"
            if habit_key in st.session_state.get('streak_messages', {}):
                message, msg_type = st.session_state.streak_messages[habit_key]
                if msg_type == "success":
                    st.success(message)
                elif msg_type == "info":
                    st.info(message)
                elif msg_type == "warning":
                    st.warning(message)
                del st.session_state.streak_messages[habit_key]
            progress_html = ""
            current_progress = habit[6] % 5
            for i in range(5):
                if i < current_progress:
                    progress_html += "<div class='progress-segment active'></div>"
                else:
                    progress_html += "<div class='progress-segment'></div>"
            col1, col2 = st.columns([1, 7])
            with col1:
                button1 = st.button("Done!", key=f"track_{habit[0]}")
                button2 = st.button("↺", key=f"reset_{habit[0]}")
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
                    st.session_state.setdefault('streak_messages', {})[habit_key] = (success_message, "success")
                else:
                    st.session_state.setdefault('streak_messages', {})[habit_key] = (success_message, "info")
            if button2:
                reset_message = reset_habit_streak(habit[0])
                st.session_state.setdefault('streak_messages', {})[habit_key] = (reset_message, "warning")
    else:
        st.info("No habits tracked yet. Add your first habit above! 🎯")

if 'username' not in st.session_state:
    page = st.selectbox("Select Page", ["Login", "Register"])
    if page == "Login":
        login_page()
    else:
        register_page()
else:
    if st.session_state.get('page', 'main') == 'main':
        main_page()
    elif st.session_state['page'] == 'profile':
        profile_page()
