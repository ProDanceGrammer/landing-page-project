import psycopg2
import psycopg2.extras
import json
import re
import os
from datetime import datetime
from typing import Optional


def get_connection():
    """Get PostgreSQL connection from DATABASE_URL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required for PostgreSQL")
    return psycopg2.connect(database_url)


def init_database():
    """Initialize PostgreSQL database with leads table"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            received_at TIMESTAMP DEFAULT NOW(),
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
    cursor.close()
    conn.close()


def normalize_data(lead_data: dict) -> dict:
    """Normalize lead data (same logic as SQLite version)"""
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
    db_path: str = None  # Ignored for PostgreSQL, kept for compatibility
) -> int:
    """Save lead to PostgreSQL database"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads (
            raw_json, name, email, phone, company, message,
            ai_summary, temperature, priority_score, classification_reasoning, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
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

    lead_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()

    return lead_id


def get_lead(lead_id: int, db_path: str = None) -> Optional[dict]:
    """Get lead by ID from PostgreSQL"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM leads WHERE id = %s", (lead_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return dict(row)
    return None


def get_all_leads(limit: int = 100, offset: int = 0, db_path: str = None) -> list[dict]:
    """Get all leads from PostgreSQL with pagination"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "SELECT * FROM leads ORDER BY received_at DESC LIMIT %s OFFSET %s",
        (limit, offset)
    )
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in rows]
