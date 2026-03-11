import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    full_name TEXT,
    product TEXT,
    phone TEXT,
    country TEXT,
    region TEXT,
    address TEXT
)
""")

conn.commit()
