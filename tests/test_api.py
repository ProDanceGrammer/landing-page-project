import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from main import app
from models import LeadClassification


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_config():
    with patch('main.config') as mock_cfg:
        mock_cfg.DATABASE_PATH = ":memory:"
        mock_cfg.AI_BACKEND = "ollama"
        mock_cfg.OLLAMA_BASE_URL = "http://localhost:11434"
        mock_cfg.TELEGRAM_BOT_TOKEN = "test-token"
        mock_cfg.TELEGRAM_CHAT_ID = "test-chat-id"
        yield mock_cfg


@pytest.fixture
def mock_ai_service():
    with patch('main.ai_service') as mock_ai:
        mock_ai.generate_summary = AsyncMock(return_value="Test AI summary")
        mock_ai.classify_lead = AsyncMock(return_value=LeadClassification(
            temperature="Hot",
            priority_score=85,
            reasoning="Clear need with urgency"
        ))
        yield mock_ai


@pytest.fixture
def mock_telegram():
    with patch('telegram_notifier.send_lead_notification') as mock_tg:
        mock_tg.return_value = AsyncMock()
        yield mock_tg


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_create_lead_success(client, mock_config, mock_ai_service, mock_telegram):
    with patch('main.save_lead') as mock_save, \
         patch('main.get_lead') as mock_get:

        mock_save.return_value = 1
        mock_get.return_value = {
            "id": 1,
            "received_at": "2026-06-08T11:00:00",
            "raw_json": '{"name": "John Smith"}',
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+15551234567",
            "company": "TechCorp",
            "message": "Need solution",
            "ai_summary": "Test summary",
            "temperature": "Hot",
            "priority_score": 85,
            "classification_reasoning": "Clear need",
            "status": "processed"
        }

        payload = {
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "company": "TechCorp",
            "message": "We need an enterprise solution ASAP"
        }

        response = client.post("/api/leads", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["status"] == "processed"
        assert data["ai_summary"] == "Test AI summary"
        assert data["classification"]["temperature"] == "Hot"
        assert data["classification"]["priority_score"] == 85


def test_create_lead_invalid_email(client):
    payload = {
        "name": "John Smith",
        "email": "invalid-email",
        "message": "Test message"
    }

    response = client.post("/api/leads", json=payload)

    assert response.status_code == 422


def test_create_lead_missing_required_field(client):
    payload = {
        "name": "John Smith",
        "email": "john@example.com"
    }

    response = client.post("/api/leads", json=payload)

    assert response.status_code == 422


def test_get_lead_by_id_success(client, mock_config):
    with patch('main.get_lead') as mock_get:
        mock_get.return_value = {
            "id": 1,
            "received_at": "2026-06-08T11:00:00",
            "raw_json": '{"name": "Jane Doe", "email": "jane@example.com", "message": "Test"}',
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": None,
            "company": None,
            "message": "Test",
            "ai_summary": "Summary",
            "temperature": "Warm",
            "priority_score": 60,
            "classification_reasoning": "Needs follow-up",
            "status": "processed"
        }

        response = client.get("/api/leads/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["normalized_data"]["email"] == "jane@example.com"


def test_get_lead_by_id_not_found(client, mock_config):
    with patch('main.get_lead') as mock_get:
        mock_get.return_value = None

        response = client.get("/api/leads/999")

        assert response.status_code == 404


def test_list_leads(client, mock_config):
    with patch('main.get_all_leads') as mock_list:
        mock_list.return_value = [
            {
                "id": 1,
                "received_at": "2026-06-08T11:00:00",
                "raw_json": '{"name": "Lead 1", "email": "lead1@example.com", "message": "Test"}',
                "name": "Lead 1",
                "email": "lead1@example.com",
                "phone": None,
                "company": None,
                "message": "Test",
                "ai_summary": "Summary 1",
                "temperature": "Hot",
                "priority_score": 90,
                "classification_reasoning": "Urgent",
                "status": "processed"
            },
            {
                "id": 2,
                "received_at": "2026-06-08T10:00:00",
                "raw_json": '{"name": "Lead 2", "email": "lead2@example.com", "message": "Test"}',
                "name": "Lead 2",
                "email": "lead2@example.com",
                "phone": None,
                "company": None,
                "message": "Test",
                "ai_summary": "Summary 2",
                "temperature": "Cold",
                "priority_score": 30,
                "classification_reasoning": "Low priority",
                "status": "processed"
            }
        ]

        response = client.get("/api/leads?limit=10&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == 1
        assert data[1]["id"] == 2


def test_list_leads_limit_validation(client):
    response = client.get("/api/leads?limit=1000")

    assert response.status_code == 400


def test_health_check(client, mock_config):
    with patch('main.get_all_leads'), \
         patch('httpx.AsyncClient') as mock_httpx, \
         patch('telegram.Bot') as mock_bot:

        mock_response = Mock()
        mock_response.status_code = 200
        mock_httpx.return_value.__aenter__.return_value.get = AsyncMock(return_value=mock_response)

        mock_bot_instance = Mock()
        mock_bot_instance.get_me = AsyncMock()
        mock_bot.return_value = mock_bot_instance

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
