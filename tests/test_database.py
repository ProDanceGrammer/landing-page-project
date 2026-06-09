import pytest
import sqlite3
import json
import tempfile
import os
from database import init_database, normalize_data, save_lead, get_lead, get_all_leads


@pytest.fixture
def test_db():
    # Use temporary file instead of :memory: to persist across connections
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    init_database(db_path)
    yield db_path
    os.unlink(db_path)


def test_init_database(test_db):
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[0] == "leads"


def test_normalize_data():
    raw_data = {
        "name": "  john smith  ",
        "email": "  John.Smith@EXAMPLE.COM  ",
        "phone": "+1-555-123-4567",
        "company": "  tech corp inc  ",
        "message": "  Looking for a solution  "
    }

    normalized = normalize_data(raw_data)

    assert normalized["name"] == "John Smith"
    assert normalized["email"] == "john.smith@example.com"
    assert normalized["phone"] == "+15551234567"
    assert normalized["company"] == "Tech Corp Inc"
    assert normalized["message"] == "Looking for a solution"


def test_save_and_get_lead(test_db):
    raw_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+15559998888",
        "company": "Startup Inc",
        "message": "Need enterprise solution"
    }

    normalized = normalize_data(raw_data)

    lead_id = save_lead(
        raw_data=raw_data,
        normalized_data=normalized,
        ai_summary="Test summary",
        temperature="Hot",
        priority_score=85,
        reasoning="High urgency",
        db_path=test_db
    )

    assert lead_id > 0

    lead = get_lead(lead_id, test_db)

    assert lead is not None
    assert lead["id"] == lead_id
    assert lead["name"] == "Jane Doe"
    assert lead["email"] == "jane@example.com"
    assert lead["temperature"] == "Hot"
    assert lead["priority_score"] == 85
    assert lead["ai_summary"] == "Test summary"
    assert lead["classification_reasoning"] == "High urgency"


def test_get_all_leads(test_db):
    for i in range(5):
        raw_data = {
            "name": f"Lead {i}",
            "email": f"lead{i}@example.com",
            "message": f"Message {i}"
        }
        normalized = normalize_data(raw_data)
        save_lead(
            raw_data=raw_data,
            normalized_data=normalized,
            ai_summary=f"Summary {i}",
            temperature="Warm",
            priority_score=50,
            reasoning="Test",
            db_path=test_db
        )

    leads = get_all_leads(limit=10, offset=0, db_path=test_db)

    assert len(leads) == 5
    lead_names = [lead["name"] for lead in leads]
    assert "Lead 0" in lead_names
    assert "Lead 4" in lead_names


def test_get_lead_not_found(test_db):
    lead = get_lead(999, test_db)
    assert lead is None


def test_normalize_data_with_missing_fields():
    raw_data = {
        "name": "John",
        "email": "john@example.com",
        "message": "Hello"
    }

    normalized = normalize_data(raw_data)

    assert normalized["name"] == "John"
    assert normalized["email"] == "john@example.com"
    assert normalized["message"] == "Hello"
    assert "phone" not in normalized
    assert "company" not in normalized
