import sqlite3
import os

db_path = "database/attendance.db"

print("Database path:", os.path.abspath(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables:", tables)

conn.close()