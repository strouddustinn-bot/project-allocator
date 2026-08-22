from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .decision import Evaluation
from .models import Project


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    decision TEXT NOT NULL,
    score INTEGER NOT NULL,
    confidence TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    blockers_json TEXT NOT NULL,
    next_action TEXT NOT NULL,
    authorized_cash REAL NOT NULL,
    authorized_hours REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS experiment_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    outcome TEXT NOT NULL,
    actual_cash REAL NOT NULL DEFAULT 0,
    actual_hours REAL NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_evaluations_project_name
    ON evaluations(project_name, id DESC);

CREATE INDEX IF NOT EXISTS idx_results_project_name
    ON experiment_results(project_name, id DESC);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def save_project(conn: sqlite3.Connection, project: Project) -> None:
    payload = json.dumps(project.to_dict(), default=str)
    conn.execute(
        """
        INSERT INTO projects(name, payload_json)
        VALUES (?, ?)
        ON CONFLICT(name) DO UPDATE SET
            payload_json=excluded.payload_json,
            updated_at=CURRENT_TIMESTAMP
        """,
        (project.name, payload),
    )
    conn.commit()


def save_evaluation(conn: sqlite3.Connection, project_name: str, evaluation: Evaluation) -> None:
    conn.execute(
        """
        INSERT INTO evaluations(
            project_name, decision, score, confidence, reasons_json,
            blockers_json, next_action, authorized_cash, authorized_hours
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_name,
            evaluation.decision.value,
            evaluation.score,
            evaluation.confidence.value,
            json.dumps(evaluation.reasons),
            json.dumps(evaluation.blockers),
            evaluation.next_action,
            evaluation.authorized_cash,
            evaluation.authorized_hours,
        ),
    )
    conn.commit()


def list_latest(conn: sqlite3.Connection):
    return conn.execute(
        """
        SELECT e.*
        FROM evaluations e
        JOIN (
            SELECT project_name, MAX(id) AS max_id
            FROM evaluations
            GROUP BY project_name
        ) latest ON e.id = latest.max_id
        ORDER BY score DESC, project_name ASC
        """
    ).fetchall()


def record_result(
    conn: sqlite3.Connection,
    project_name: str,
    outcome: str,
    actual_cash: float = 0.0,
    actual_hours: float = 0.0,
    notes: str = "",
) -> None:
    conn.execute(
        """
        INSERT INTO experiment_results(project_name, outcome, actual_cash, actual_hours, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_name, outcome, actual_cash, actual_hours, notes),
    )
    conn.commit()
