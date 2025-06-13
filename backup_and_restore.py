import sqlite3
import json
from datetime import datetime

def backup_data():
    # Connect to the database
    conn = sqlite3.connect('compensation_rates.db')
    cursor = conn.cursor()
    
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Dictionary to store all data
    data = {}
    
    # For each table, get all data
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # Skip sqlite internal table
            cursor.execute(f"SELECT * FROM {table_name}")
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            data[table_name] = {
                'columns': columns,
                'rows': [list(row) for row in rows]
            }
    
    # Save data to JSON file
    with open('database_backup.json', 'w') as f:
        json.dump(data, f, default=str)
    
    conn.close()
    print("Backup completed to database_backup.json")

def drop_tables():
    conn = sqlite3.connect('compensation_rates.db')
    cursor = conn.cursor()
    
    # Get list of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Drop each table
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # Skip sqlite internal table
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    conn.commit()
    conn.close()
    print("All tables dropped successfully")

if __name__ == "__main__":
    print("Starting backup process...")
    backup_data()
    print("Starting table drop process...")
    drop_tables()
    print("Process completed!") 