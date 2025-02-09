# database.py
import sqlite3
import time

def create_connection():
    conn = sqlite3.connect('user_data.db')
    return conn

def create_user_table():
    conn = create_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, 
                     password TEXT,
                     display_name TEXT,
                     bio TEXT,
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

def create_tabs_table():
    conn = create_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS tabs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        title TEXT,
                        url TEXT,
                        duration REAL,
                        timestamp INTEGER,
                        FOREIGN KEY (username) REFERENCES users(username)
                    )''')
    conn.commit()
    conn.close()

def update_tabs_table(tab_list):
    if not tab_list:
         return
    conn = create_connection()
    cursor = conn.cursor()
    # Get the username from the first item and strip any extra spaces.
    username = tab_list[0].get('username')
    print(f"hey user: {username}")
    if username:
         username = username.strip()
         cursor.execute("DELETE FROM tabs WHERE username = ?", (username,))
    for tab in tab_list:
         # Also strip username before inserting.
         u = tab.get('username')
         if u:
             u = u.strip()
         cursor.execute(
             "INSERT INTO tabs (username, title, url, duration, timestamp) VALUES (?, ?, ?, ?, ?)",
             (u, tab['title'], tab['url'], tab['duration'], int(time.time()))
         )
    conn.commit()
    conn.close()

def upgrade_database():
    conn = create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('PRAGMA table_info(users)')
        columns = [column[1] for column in cursor.fetchall()]
        if 'display_name' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN display_name TEXT')
            conn.execute('UPDATE users SET display_name = username')
        if 'bio' not in columns:
            conn.execute('ALTER TABLE users ADD COLUMN bio TEXT')
            conn.execute('UPDATE users SET bio = ?', ("No bio yet.",))
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

def store_user(username, password):
    conn = create_connection()
    conn.execute('''INSERT INTO users 
                    (username, password, login_count, display_name, bio) 
                    VALUES (?, ?, ?, ?, ?)''', 
                 (username, password, 0, username, "No bio yet."))
    conn.commit()
    conn.close()

def get_user(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_stats(username):
    conn = create_connection()
    conn.execute('UPDATE users SET login_count = login_count + 1 WHERE username=?', (username,))
    conn.commit()
    conn.close()

def update_user_profile(username, display_name=None, bio=None):
    conn = create_connection()
    if display_name is not None:
        conn.execute('UPDATE users SET display_name = ? WHERE username = ?', 
                    (display_name, username))
    if bio is not None:
        conn.execute('UPDATE users SET bio = ? WHERE username = ?', 
                    (bio, username))
    conn.commit()
    conn.close()

def update_tabs_table(tab_list):
    conn = create_connection()
    cursor = conn.cursor()
    # For simplicity, clear the old data before inserting the new tab stats.
    cursor.execute("DELETE FROM tabs")
    for tab in tab_list:
        cursor.execute("INSERT INTO tabs (title, url, duration, timestamp) VALUES (?, ?, ?, ?)",
                       (tab['title'], tab['url'], tab['duration'], int(time.time())))
    conn.commit()
    conn.close()

def get_tabs(username):
    conn = create_connection()
    cursor = conn.cursor()
    username = username.strip()  # Ensure no extra spaces.
    print(f"Querying tabs for username: {username}")
    cursor.execute("SELECT title, url, duration, timestamp FROM tabs WHERE username=?", (username,))
    rows = cursor.fetchall()
    print(f"Found {len(rows)} tab rows.")
    conn.close()
    return rows

# debugging purpose
def print_all_content():
    """Connects to an SQLite database and prints all content from the specified table."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM {'tabs'}")
        rows = cursor.fetchall()
        
        for row in rows:
            print(row)
        
        conn.close()
    except sqlite3.Error as e:
        print(f"Error: {e}")
