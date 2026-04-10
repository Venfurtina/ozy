import sqlite3

DB = "takvim.db"

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.executescript(
    """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS reset_tokens;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    color TEXT
);

CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    color TEXT,
    username TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(date, user_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    comment TEXT NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    token TEXT
);
"""
)

conn.commit()
conn.close()
print("✅ Veritabanı başarıyla oluşturuldu:", DB)
