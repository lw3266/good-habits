import sqlite3

def print_database_contents(db_path):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if not tables:
        print("No tables found in the database.")
        return

    # Iterate over tables and print their contents
    for table_name in tables:
        table = table_name[0]
        print(f"\nTable: {table}")
        print("-" * 40)

        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        print(" | ".join(columns))  # Print column headers
        print("-" * 40)

        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()

        for row in rows:
            print(" | ".join(map(str, row)))

    # Close the connection
    conn.close()

# Example usage
db_path = "user_data.db"  # Replace with your database file path
print_database_contents(db_path)
