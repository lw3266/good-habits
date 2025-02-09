import random
from database import create_connection  # Ensure this is defined in database.py

# --- Habit Tracking Functions ---

def add_habit(username, habit_name, target_frequency):
    """
    Add a new habit for the given user.
    """
    conn = create_connection()
    conn.execute(
        '''INSERT INTO habits 
           (username, habit_name, target_frequency, created_date, streak) 
           VALUES (?, ?, ?, DATE('now'), 0)''', 
        (username, habit_name, target_frequency)
    )
    conn.commit()
    conn.close()


def get_user_habits(username):
    """
    Retrieve all habits associated with the given username.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM habits WHERE username=?', (username,))
    habits = cursor.fetchall()
    conn.close()
    return habits


def get_streak_increment_message(streak):
    """
    Return a congratulatory message based on the new streak value.
    If the streak is a multiple of 5, return a milestone message.
    Otherwise, return a regular encouragement.
    """
    if streak % 5 == 0:
        milestone_messages = [
            f"🎉 INCREDIBLE! {streak} DAYS! You've earned another 🔥! Your dedication is absolutely inspiring!",
            f"🌟 PHENOMENAL! {streak} days and another 🔥 added to your collection! You're becoming unstoppable!",
            f"⭐ LEGENDARY STATUS! {streak} days and a new 🔥! You're what consistency looks like!",
            f"🏆 BOOM! {streak} days and you've unlocked another 🔥! You're building an empire of good habits!",
            f"🎯 MAGNIFICENT! {streak} days strong! Another 🔥 to show for your incredible journey!"
        ]
        return random.choice(milestone_messages)
    
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
    """
    Increment the streak of the habit with the given ID.
    Returns an appropriate congratulatory message.
    """
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT streak FROM habits WHERE id=?', (habit_id,))
    result = cursor.fetchone()
    if result is None:
        conn.close()
        return "Habit not found."
    current_streak = result[0]
    conn.execute(
        '''UPDATE habits 
           SET streak = streak + 1,
               last_tracked = DATE('now')
           WHERE id=?''', 
        (habit_id,)
    )
    conn.commit()
    conn.close()
    return get_streak_increment_message(current_streak + 1)


def get_reset_message():
    """
    Return a motivational message when a habit streak is reset.
    """
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
    """
    Reset the streak for the given habit to zero.
    Returns a reset message.
    """
    conn = create_connection()
    conn.execute('UPDATE habits SET streak = 0 WHERE id=?', (habit_id,))
    conn.commit()
    conn.close()
    return get_reset_message()


def get_streak_display(streak):
    """
    Return a string representation of the streak including fire emojis.
    One fire emoji is added for every 5 days of streak.
    """
    fire_emojis = '🔥' * (streak // 5)
    return f"{streak} {fire_emojis}"
