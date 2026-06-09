import pytest
from unittest.mock import Mock, AsyncMock, patch
from models import LeadClassification
from ai_service import OllamaService, OpenAIService, get_ai_service
from config import Config


@pytest.fixture
def ollama_config():
    config = Mock(spec=Config)
    config.AI_BACKEND = "ollama"
    config.OLLAMA_MODEL = "llama3"
    config.OLLAMA_BASE_URL = "http://localhost:11434"
    return config


@pytest.fixture
def openai_config():
    config = Mock(spec=Config)
    config.AI_BACKEND = "openai"
    config.OPENAI_API_KEY = "sk-test-key"
    config.OPENAI_MODEL = "gpt-3.5-turbo"
    return config


@pytest.mark.asyncio
async def test_ollama_generate_summary(ollama_config):
    with patch('httpx.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": [{"name": "llama3"}]}

        service = OllamaService(ollama_config)

        lead_data = {
            "name": "John Smith",
            "company": "TechCorp",
            "message": "Need enterprise solution ASAP"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "response": "TechCorp needs an enterprise solution with urgency."
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            summary = await service.generate_summary(lead_data)

            assert summary == "TechCorp needs an enterprise solution with urgency."
            mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_classify_lead(ollama_config):
    with patch('httpx.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": [{"name": "llama3"}]}

        service = OllamaService(ollama_config)

        lead_data = {
            "name": "John Smith",
            "company": "TechCorp",
            "message": "Need it urgently"
        }

        with patch('httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "response": '{"temperature": "Hot", "priority_score": 90, "reasoning": "Urgent need indicated"}'
            }

            mock_post = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.post = mock_post

            classification = await service.classify_lead(lead_data, "Summary")

            assert classification.temperature == "Hot"
            assert classification.priority_score == 90
            assert "Urgent" in classification.reasoning


@pytest.mark.asyncio
async def test_ollama_fallback_on_error(ollama_config):
    with patch('httpx.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": [{"name": "llama3"}]}

        service = OllamaService(ollama_config)

        lead_data = {"name": "Test", "message": "Test message"}

        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock(side_effect=Exception("Connection error"))
            mock_client.return_value.__aenter__.return_value.post = mock_post

            summary = await service.generate_summary(lead_data)
            assert summary == "AI summary unavailable"

            classification = await service.classify_lead(lead_data, "test")
            assert classification.temperature == "Warm"
            assert classification.priority_score == 50


@pytest.mark.asyncio
async def test_openai_generate_summary(openai_config):
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="AI generated summary"))]

        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        service = OpenAIService(openai_config)

        lead_data = {
            "name": "Jane Doe",
            "company": "Startup Inc",
            "message": "Looking for demo"
        }

        summary = await service.generate_summary(lead_data)

        assert summary == "AI generated summary"


@pytest.mark.asyncio
async def test_openai_classify_lead(openai_config):
    with patch('openai.AsyncOpenAI') as mock_openai:
        mock_client = Mock()
        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(
            content='{"temperature": "Warm", "priority_score": 60, "reasoning": "Needs follow-up"}'
        ))]

        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_openai.return_value = mock_client

        service = OpenAIService(openai_config)

        lead_data = {"name": "Test", "message": "Interested"}

        classification = await service.classify_lead(lead_data, "Summary")

        assert classification.temperature == "Warm"
        assert classification.priority_score == 60


def test_get_ai_service_ollama(ollama_config):
    with patch('httpx.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"models": []}

        service = get_ai_service(ollama_config)

        assert isinstance(service, OllamaService)


def test_get_ai_service_openai(openai_config):
    with patch('openai.AsyncOpenAI'):
        service = get_ai_service(openai_config)

        assert isinstance(service, OpenAIService)


def test_get_ai_service_invalid_backend():
    config = Mock(spec=Config)
    config.AI_BACKEND = "invalid"

    with pytest.raises(ValueError, match="Unknown AI backend"):
        get_ai_service(config)
