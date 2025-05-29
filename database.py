import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('subscriptions.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER PRIMARY KEY,
    expire_date TEXT
)
''')
conn.commit()

def add_subscription(user_id, months):
    now = datetime.now()
    expire = now + timedelta(days=30 * months)
    cursor.execute("REPLACE INTO subscriptions (user_id, expire_date) VALUES (?, ?)", (user_id, expire.isoformat()))
    conn.commit()

def extend_subscription(user_id, months):
    cursor.execute("SELECT expire_date FROM subscriptions WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    now = datetime.now()
    if row:
        expire = max(now, datetime.fromisoformat(row[0])) + timedelta(days=30 * months)
    else:
        expire = now + timedelta(days=30 * months)
    cursor.execute("REPLACE INTO subscriptions (user_id, expire_date) VALUES (?, ?)", (user_id, expire.isoformat()))
    conn.commit()
    return expire

def get_users():
    cursor.execute("SELECT user_id, expire_date FROM subscriptions")
    return cursor.fetchall()

def delete_subscription(user_id):
    cursor.execute("DELETE FROM subscriptions WHERE user_id=?", (user_id,))
    conn.commit()