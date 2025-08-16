# src/databases/db_sqls.py
from src import my_constants as constants

IGNORE_UID = f"""
CREATE TABLE IF NOT EXISTS {constants.TABLE_IGNORE_UID} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
)
"""
IGNORE_PHONE_NUMBER = f"""
CREATE TABLE IF NOT EXISTS {constants.TABLE_IGNORE_PHONE_NUMBER} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT UNIQUE NOT NULL,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
)
"""
RESULT = f"""
CREATE TABLE IF NOT EXISTS {constants.TABLE_RESULTS} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_url TEXT,
    article_content TEXT,
    author_url TEXT,
    author_name TEXT,
    contact TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now'))
)
"""
