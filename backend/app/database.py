from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .config import settings

DB_PATH = Path(settings.database_url.replace("sqlite:///", ""))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('admin','qa_user')),
          active INTEGER NOT NULL DEFAULT 1,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS matrix_versions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          filename TEXT NOT NULL,
          sha256 TEXT NOT NULL,
          uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          activated_at TEXT,
          sheet_count INTEGER NOT NULL DEFAULT 0,
          rule_count INTEGER NOT NULL DEFAULT 0,
          active INTEGER NOT NULL DEFAULT 0,
          index_ready INTEGER NOT NULL DEFAULT 0,
          path TEXT NOT NULL,
          UNIQUE(sha256)
        );
        CREATE TABLE IF NOT EXISTS matrix_records (
          id TEXT PRIMARY KEY,
          matrix_version_id INTEGER NOT NULL,
          workbook TEXT NOT NULL,
          sheet TEXT NOT NULL,
          category TEXT,
          subcategory TEXT,
          rule TEXT NOT NULL,
          instructions TEXT,
          metadata_json TEXT NOT NULL,
          source_row_start INTEGER,
          source_row_end INTEGER,
          cell_range TEXT,
          score REAL,
          critical INTEGER NOT NULL DEFAULT 0,
          critical_condition TEXT,
          FOREIGN KEY(matrix_version_id) REFERENCES matrix_versions(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_records_matrix ON matrix_records(matrix_version_id);
        CREATE INDEX IF NOT EXISTS idx_records_sheet ON matrix_records(sheet);
        CREATE TABLE IF NOT EXISTS chats (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER NOT NULL,
          title TEXT NOT NULL DEFAULT 'New Chat',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS messages (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          chat_id INTEGER NOT NULL,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          payload_json TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS runtime_settings (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS audit_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          event TEXT NOT NULL,
          detail TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
