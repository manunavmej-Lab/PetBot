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
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    pet_id TEXT NOT NULL REFERENCES pets(id),
    type TEXT NOT NULL,
    content TEXT NOT NULL,
    normalized_content TEXT NOT NULL,
    importance REAL NOT NULL CHECK (importance BETWEEN 0 AND 1),
    confidence REAL NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    source TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_accessed_at TEXT NOT NULL,
    expires_at TEXT
);
CREATE INDEX IF NOT EXISTS memories_by_pet ON memories(pet_id, type, created_at DESC);
CREATE INDEX IF NOT EXISTS memories_expiration ON memories(expires_at);
CREATE TABLE IF NOT EXISTS known_people (
    id TEXT PRIMARY KEY,
    pet_id TEXT NOT NULL REFERENCES pets(id),
    display_name TEXT NOT NULL,
    face_embedding TEXT NOT NULL,
    consented_at TEXT NOT NULL,
    UNIQUE(pet_id, display_name)
);
CREATE TABLE IF NOT EXISTS pet_lifecycle (
    pet_id TEXT PRIMARY KEY REFERENCES pets(id),
    last_tick_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pet_autonomy (
    pet_id TEXT PRIMARY KEY REFERENCES pets(id),
    mode TEXT NOT NULL,
    is_sleeping INTEGER NOT NULL CHECK (is_sleeping IN (0, 1))
);
"""


def connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection
