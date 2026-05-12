import sqlite3

DB_PATH = "words.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, player TEXT)")

def save_word(word: str, player: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO words (word, player) VALUES (?, ?)", (word.lower(), player))

def get_all_words():
    with sqlite3.connect(DB_PATH) as conn:
        return [row[0] for row in conn.execute("SELECT word FROM words ORDER BY id").fetchall()]

def get_word_count():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]

def get_last_word():
    with sqlite3.connect(DB_PATH) as conn:
        res = conn.execute("SELECT word FROM words ORDER BY id DESC LIMIT 1").fetchone()
        return res[0] if res else None

def clear_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM words")

