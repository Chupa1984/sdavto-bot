import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            phone TEXT,
            time TEXT,
            auto TEXT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_booking(user_id, name, phone, time, auto="не указано"):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (user_id, name, phone, time, auto) VALUES (?, ?, ?, ?, ?)",
                   (user_id, name, phone, time, auto))
    conn.commit()
    conn.close()
