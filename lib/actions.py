import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

DB_PATH = "data/state.db"

SCHEMA = [
    "PRAGMA journal_mode=WAL;",
    "CREATE TABLE IF NOT EXISTS actions (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        ts TEXT NOT NULL,\n        user_id TEXT NOT NULL,\n        entity_id TEXT NOT NULL,\n        action_type TEXT NOT NULL,\n        payload TEXT\n    );",
    "CREATE INDEX IF NOT EXISTS idx_actions_ts ON actions(ts);",
    "CREATE INDEX IF NOT EXISTS idx_actions_entity ON actions(entity_id);",
    "CREATE TABLE IF NOT EXISTS notes (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        ts TEXT NOT NULL,\n        user_id TEXT NOT NULL,\n        entity_id TEXT NOT NULL,\n        note_text TEXT NOT NULL,\n        follow_up_date TEXT\n    );",
    "CREATE INDEX IF NOT EXISTS idx_notes_entity ON notes(entity_id);",
    "CREATE TABLE IF NOT EXISTS entity_state (\n        entity_id TEXT PRIMARY KEY,\n        skipped INTEGER NOT NULL DEFAULT 0,\n        last_action_ts TEXT\n    );",
    "CREATE TABLE IF NOT EXISTS readiness (\n        entity_id TEXT PRIMARY KEY,\n        ts TEXT NOT NULL,\n        answers TEXT NOT NULL,\n        score REAL NOT NULL,\n        level TEXT NOT NULL\n    );",
    "CREATE INDEX IF NOT EXISTS idx_readiness_level ON readiness(level);"
]

def get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    own = False
    if conn is None:
        conn = get_conn()
        own = True
    try:
        cur = conn.cursor()
        for sql in SCHEMA:
            cur.execute(sql)
        conn.commit()
    finally:
        if own:
            conn.close()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def log_action(user_id: str, entity_id: str, action_type: str, payload: Optional[Dict[str, Any]] = None) -> int:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    ts = _now_iso()
    cur.execute(
        "INSERT INTO actions(ts, user_id, entity_id, action_type, payload) VALUES(?,?,?,?,?)",
        (ts, user_id, entity_id, action_type, json.dumps(payload or {}))
    )
    # upsert entity_state
    cur.execute(
        "INSERT INTO entity_state(entity_id, skipped, last_action_ts) VALUES(?,?,?)\n         ON CONFLICT(entity_id) DO UPDATE SET last_action_ts=excluded.last_action_ts",
        (entity_id, 0, ts)
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def append_note(user_id: str, entity_id: str, note_text: str, follow_up_date: Optional[str] = None) -> int:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    ts = _now_iso()
    cur.execute(
        "INSERT INTO notes(ts, user_id, entity_id, note_text, follow_up_date) VALUES(?,?,?,?,?)",
        (ts, user_id, entity_id, note_text, follow_up_date)
    )
    # reflect last action
    cur.execute(
        "INSERT INTO entity_state(entity_id, skipped, last_action_ts) VALUES(?,?,?)\n         ON CONFLICT(entity_id) DO UPDATE SET last_action_ts=excluded.last_action_ts",
        (entity_id, 0, ts)
    )
    conn.commit()
    rid = cur.lastrowid
    conn.close()
    return rid


def set_skip(entity_id: str, skipped: bool = True) -> None:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    ts = _now_iso()
    cur.execute(
        "INSERT INTO entity_state(entity_id, skipped, last_action_ts) VALUES(?,?,?)\n         ON CONFLICT(entity_id) DO UPDATE SET skipped=excluded.skipped, last_action_ts=excluded.last_action_ts",
        (entity_id, 1 if skipped else 0, ts)
    )
    conn.commit()
    conn.close()


def get_notes(entity_id: str) -> List[sqlite3.Row]:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE entity_id=? ORDER BY ts DESC", (entity_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_actions(entity_id: str) -> List[sqlite3.Row]:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM actions WHERE entity_id=? ORDER BY ts DESC", (entity_id,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_actions_by_range(start_iso: str, end_iso: str) -> List[sqlite3.Row]:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM actions WHERE ts BETWEEN ? AND ? ORDER BY ts ASC", (start_iso, end_iso))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_notes_by_range(start_iso: str, end_iso: str) -> List[sqlite3.Row]:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE ts BETWEEN ? AND ? ORDER BY ts ASC", (start_iso, end_iso))
    rows = cur.fetchall()
    conn.close()
    return rows

# Readiness overlay -----------------------------------------------------------

def set_readiness(entity_id: str, answers: Dict[str, Any], score: float, level: str) -> None:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    ts = _now_iso()
    cur.execute(
        "INSERT INTO readiness(entity_id, ts, answers, score, level) VALUES(?,?,?,?,?)\n         ON CONFLICT(entity_id) DO UPDATE SET ts=excluded.ts, answers=excluded.answers, score=excluded.score, level=excluded.level",
        (entity_id, ts, json.dumps(answers or {}), float(score), str(level))
    )
    # reflect last action
    cur.execute(
        "INSERT INTO entity_state(entity_id, skipped, last_action_ts) VALUES(?,?,?)\n         ON CONFLICT(entity_id) DO UPDATE SET last_action_ts=excluded.last_action_ts",
        (entity_id, 0, ts)
    )
    conn.commit()
    conn.close()


def get_readiness(entity_id: str) -> Optional[sqlite3.Row]:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM readiness WHERE entity_id=?", (entity_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_all_readiness() -> List[sqlite3.Row]:
    conn = get_conn()
    init_db(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM readiness")
    rows = cur.fetchall()
    conn.close()
    return rows
