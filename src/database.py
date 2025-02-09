import sqlite3
import os

def create_connection():
    # Get the absolute path to the src directory
    src_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(src_dir, 'user_data.db')
    conn = sqlite3.connect(db_path)
    return conn

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

def create_user_table():
    conn = create_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (username TEXT PRIMARY KEY, 
                    password TEXT, 
                    login_count INTEGER,
                    display_name TEXT,
                    bio TEXT)''')
    conn.commit()
    conn.close()
    upgrade_database()

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
