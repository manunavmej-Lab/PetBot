from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS pets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
    schema_version INTEGER NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_pet ON pets(is_active) WHERE is_active = 1;
CREATE TABLE IF NOT EXISTS personality_traits (
    pet_id TEXT NOT NULL REFERENCES pets(id),
    trait TEXT NOT NULL,
    base_value INTEGER NOT NULL CHECK (base_value BETWEEN 0 AND 100),
    current_value INTEGER NOT NULL CHECK (current_value BETWEEN 0 AND 100),
    min_value INTEGER NOT NULL DEFAULT 0,
    max_value INTEGER NOT NULL DEFAULT 100,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (pet_id, trait)
);
CREATE TABLE IF NOT EXISTS emotional_states (
    pet_id TEXT NOT NULL REFERENCES pets(id),
    emotion TEXT NOT NULL,
    value INTEGER NOT NULL CHECK (value BETWEEN 0 AND 100),
    updated_at TEXT NOT NULL,
    PRIMARY KEY (pet_id, emotion)
);
CREATE TABLE IF NOT EXISTS personality_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id TEXT NOT NULL REFERENCES pets(id),
    trait TEXT NOT NULL,
    delta INTEGER NOT NULL,
    cause TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection
