from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable

from .bootstrap import ensure_app_db


def connect(source_db: Path | None = None, app_db: Path | None = None) -> sqlite3.Connection:
    path = ensure_app_db(source_db=source_db, app_db=app_db)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_all(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
    return conn.execute(sql, tuple(params)).fetchall()


def fetch_one(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
    return conn.execute(sql, tuple(params)).fetchone()


def scalar(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> Any:
    row = conn.execute(sql, tuple(params)).fetchone()
    return None if row is None else row[0]
