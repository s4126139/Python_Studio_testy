from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

SOURCE_DB_NAME = "immunisation (1).db"
APP_DB_NAME = "app.db"

CONTENT_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS Persona (
    slug TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    headline TEXT NOT NULL,
    demographic TEXT NOT NULL,
    needs TEXT NOT NULL,
    goals TEXT NOT NULL,
    skills TEXT NOT NULL,
    pain_points TEXT NOT NULL,
    image_path TEXT NOT NULL DEFAULT '',
    display_order INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS TeamMember (
    full_name TEXT PRIMARY KEY,
    student_number TEXT NOT NULL,
    role_label TEXT NOT NULL,
    display_order INTEGER NOT NULL UNIQUE
);
"""

PERSONA_SEED = [
    {
        "slug": "public-health-researcher",
        "name": "Dr Maya Chen",
        "headline": "Public health researcher tracking long-term vaccination gaps",
        "demographic": "Research lead, 38, works across infectious disease surveillance projects",
        "needs": "Needs fast access to trustworthy rates, comparable regions, and transparent caveats about missing records.",
        "goals": "Compare immunisation performance across countries, identify patterns, and frame evidence without overstating conclusions.",
        "skills": "High statistical literacy, moderate web confidence, and limited patience for noisy interfaces.",
        "pain_points": "Existing dashboards often hide data quality issues, overuse jargon, or make cross-region comparison slow.",
        "image_path": "",
        "display_order": 1,
    },
    {
        "slug": "policy-adviser",
        "name": "Nadia Rahman",
        "headline": "Policy adviser briefing ministers on preventable disease risk",
        "demographic": "Government analyst, 31, prepares short evidence packs for time-poor decision makers",
        "needs": "Needs concise summaries, sortable country tables, and a defensible explanation of what is global versus country-level.",
        "goals": "Spot regions that are improving, identify outliers, and turn raw numbers into balanced recommendations.",
        "skills": "Strong policy writing, moderate spreadsheet skills, and low tolerance for technical friction.",
        "pain_points": "Manual spreadsheet work is slow, and many public sources require too much interpretation before briefing use.",
        "image_path": "",
        "display_order": 2,
    },
    {
        "slug": "medical-student",
        "name": "Elias Morgan",
        "headline": "Medical student building context around vaccines and infection trends",
        "demographic": "Final-year student, 24, uses public data to connect clinical learning with population health",
        "needs": "Needs plain-language guidance, examples of how to read each view, and clear terminology around antigens and infection type.",
        "goals": "Understand the big picture first, then explore deeper tables without feeling lost.",
        "skills": "High domain curiosity, early-career data literacy, and confidence with guided web tools.",
        "pain_points": "Many datasets assume expert context and do not explain how filters change the meaning of results.",
        "image_path": "",
        "display_order": 3,
    },
]

TEAM_MEMBER_SEED = [
    {
        "full_name": "Student A",
        "student_number": "s1234567",
        "role_label": "Track A page owner",
        "display_order": 1,
    },
    {
        "full_name": "Student B",
        "student_number": "s2345678",
        "role_label": "Track B page owner",
        "display_order": 2,
    },
]


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def default_source_db(base_dir: Path | None = None) -> Path:
    return (base_dir or project_root()) / SOURCE_DB_NAME


def default_app_db(base_dir: Path | None = None) -> Path:
    return (base_dir or project_root()) / APP_DB_NAME


def seed_content(conn: sqlite3.Connection) -> None:
    conn.executemany(
        """
        INSERT INTO Persona (
            slug, name, headline, demographic, needs, goals, skills, pain_points, image_path, display_order
        ) VALUES (
            :slug, :name, :headline, :demographic, :needs, :goals, :skills, :pain_points, :image_path, :display_order
        )
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            headline = excluded.headline,
            demographic = excluded.demographic,
            needs = excluded.needs,
            goals = excluded.goals,
            skills = excluded.skills,
            pain_points = excluded.pain_points,
            image_path = excluded.image_path,
            display_order = excluded.display_order
        """,
        PERSONA_SEED,
    )
    conn.executemany(
        """
        INSERT INTO TeamMember (
            full_name, student_number, role_label, display_order
        ) VALUES (
            :full_name, :student_number, :role_label, :display_order
        )
        ON CONFLICT(full_name) DO UPDATE SET
            student_number = excluded.student_number,
            role_label = excluded.role_label,
            display_order = excluded.display_order
        """,
        TEAM_MEMBER_SEED,
    )


def ensure_app_db(source_db: Path | None = None, app_db: Path | None = None) -> Path:
    source_path = Path(source_db) if source_db else default_source_db()
    app_path = Path(app_db) if app_db else default_app_db()

    if not source_path.exists():
        raise FileNotFoundError(f"Source database not found: {source_path}")

    if not app_path.exists():
        shutil.copyfile(source_path, app_path)

    conn = sqlite3.connect(app_path)
    try:
        conn.executescript(CONTENT_TABLES_SQL)
        seed_content(conn)
        conn.commit()
    finally:
        conn.close()

    return app_path
