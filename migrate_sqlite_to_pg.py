import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def migrate():
    """Migrate data from SQLite to PostgreSQL"""

    # Check if SQLite database exists
    if not os.path.exists('leads.db'):
        print("No leads.db found. Nothing to migrate.")
        return

    # Connect to SQLite
    print("Connecting to SQLite database...")
    sqlite_conn = sqlite3.connect('leads.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    # Check if leads table exists
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
    if not sqlite_cursor.fetchone():
        print("No 'leads' table found in SQLite database.")
        sqlite_conn.close()
        return

    # Connect to PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set!")
        print("Please add your Neon PostgreSQL connection string to .env")
        sqlite_conn.close()
        return

    print("Connecting to PostgreSQL database...")
    pg_conn = psycopg2.connect(database_url)
    pg_cursor = pg_conn.cursor()

    # Create PostgreSQL table
    print("Creating PostgreSQL table...")
    pg_cursor.execute("""
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
    pg_conn.commit()

    # Copy data
    print("Fetching leads from SQLite...")
    sqlite_cursor.execute("SELECT * FROM leads")
    rows = sqlite_cursor.fetchall()

    if not rows:
        print("No leads to migrate.")
        sqlite_conn.close()
        pg_conn.close()
        return

    print(f"Migrating {len(rows)} leads...")
    migrated = 0

    for row in rows:
        try:
            pg_cursor.execute("""
                INSERT INTO leads
                (received_at, raw_json, name, email, phone, company, message,
                 ai_summary, temperature, priority_score, classification_reasoning, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['received_at'], row['raw_json'], row['name'], row['email'],
                row['phone'], row['company'], row['message'], row['ai_summary'],
                row['temperature'], row['priority_score'],
                row['classification_reasoning'], row['status']
            ))
            migrated += 1
        except Exception as e:
            print(f"Error migrating lead ID {row['id']}: {e}")

    pg_conn.commit()
    print(f"✅ Successfully migrated {migrated} leads!")

    # Close connections
    sqlite_conn.close()
    pg_conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("SQLite to PostgreSQL Migration Script")
    print("=" * 50)
    migrate()
