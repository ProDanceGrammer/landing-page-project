import sqlite3
import json
import re
from datetime import datetime
from typing import Optional


def init_database(db_path: str = "leads.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_json TEXT NOT NULL,
            name TEXT,
            email TEXT NOT NULL,
            phone TEXT,
            company TEXT,
            message TEXT,
            ai_summary TEXT,
            temperature TEXT,
            priority_score INTEGER,
            classification_reasoning TEXT,
            status TEXT DEFAULT 'processed'
        )
    """)

    conn.commit()
    conn.close()


def normalize_data(lead_data: dict) -> dict:
    normalized = {}

    # Normalize name
    if lead_data.get("name"):
        normalized["name"] = lead_data["name"].strip().title()

    # Normalize email
    if lead_data.get("email"):
        normalized["email"] = lead_data["email"].strip().lower()

    # Normalize phone
    if lead_data.get("phone"):
        phone = lead_data["phone"]
        phone_cleaned = re.sub(r'[^\d+]', '', phone)
        normalized["phone"] = phone_cleaned

    # Normalize company
    if lead_data.get("company"):
        normalized["company"] = lead_data["company"].strip().title()

    # Normalize message
    if lead_data.get("message"):
        normalized["message"] = lead_data["message"].strip()

    return normalized


def save_lead(
    raw_data: dict,
    normalized_data: dict,
    ai_summary: str,
    temperature: str,
    priority_score: int,
    reasoning: str,
    db_path: str = "leads.db"
) -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (
            raw_json, name, email, phone, company, message,
            ai_summary, temperature, priority_score, classification_reasoning, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        json.dumps(raw_data),
        normalized_data.get("name"),
        normalized_data.get("email"),
        normalized_data.get("phone"),
        normalized_data.get("company"),
        normalized_data.get("message"),
        ai_summary,
        temperature,
        priority_score,
        reasoning,
        "processed"
    ))

    lead_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return lead_id


def get_lead(lead_id: int, db_path: str = "leads.db") -> Optional[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_all_leads(limit: int = 100, offset: int = 0, db_path: str = "leads.db") -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM leads ORDER BY received_at DESC LIMIT ? OFFSET ?",
        (limit, offset)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
