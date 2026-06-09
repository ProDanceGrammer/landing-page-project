# Lead Processing MVP

A FastAPI-based system for processing lead applications from landing pages with AI-powered summarization and classification.

## Features

- 🚀 REST API for receiving lead applications
- 🤖 Pluggable AI backends (Ollama local or OpenAI cloud)
- 📊 Automatic lead classification (Hot/Warm/Cold) with priority scoring
- 💾 SQLite database for lead storage
- 📱 Telegram notifications for new leads
- ✅ Input validation with Pydantic
- 🧪 Unit tests with pytest
- 📖 Auto-generated API documentation (Swagger/OpenAPI)

## Architecture

```
Lead Form → FastAPI API → Data Normalization → AI Service (Ollama/OpenAI)
                ↓                                       ↓
            SQLite DB ← Save Results ← Classification & Summary
                                              ↓
                                      Telegram Notification
```

**Key Components:**
- **config.py**: Environment-based configuration loader
- **models.py**: Pydantic models for request/response validation
- **database.py**: SQLite operations and data normalization
- **ai_service.py**: Abstract AI interface with Ollama and OpenAI implementations
- **telegram_notifier.py**: Telegram Bot API integration
- **main.py**: FastAPI application with all endpoints

## Prerequisites

- **Python 3.10+**
- **Ollama** (if using local AI): [Download here](https://ollama.ai/)
- **Telegram Bot Token**: Create via [@BotFather](https://t.me/botfather)

## Installation

1. **Clone or navigate to the project directory**

2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# or
.venv\Scripts\activate  # Windows CMD
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:
```env
AI_BACKEND=ollama
OLLAMA_MODEL=llama3
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

## Configuration

### AI Backend Options

**Option 1: Ollama (Local - Recommended for MVP)**
```env
AI_BACKEND=ollama
OLLAMA_MODEL=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

Install Ollama and pull a model:
```bash
ollama pull llama3
# or
ollama pull mistral
ollama pull phi3
```

**Option 2: OpenAI (Cloud)**
```env
AI_BACKEND=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### Telegram Bot Setup

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the bot token to `.env`
4. Get your chat ID:
   - Message [@userinfobot](https://t.me/userinfobot) to get your user ID
   - Or create a channel and add your bot as admin, then use channel ID

## Running the Application

1. **Start Ollama (if using local AI):**
```bash
ollama serve
```

2. **Run the FastAPI application:**
```bash
uvicorn main:app --reload
```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### `POST /api/leads`
Submit a new lead application

**Request:**
```json
{
  "name": "John Smith",
  "email": "john.smith@techcorp.com",
  "phone": "+1-555-123-4567",
  "company": "TechCorp Inc",
  "message": "We're interested in your enterprise solution..."
}
```

**Response:**
```json
{
  "id": 1,
  "received_at": "2026-06-08T11:00:00",
  "normalized_data": {...},
  "ai_summary": "TechCorp Inc is seeking an enterprise solution...",
  "classification": {
    "temperature": "Hot",
    "priority_score": 85,
    "reasoning": "Clear need with specific timeline and team size"
  },
  "status": "processed"
}
```

### `GET /api/leads/{lead_id}`
Retrieve a specific lead by ID

### `GET /api/leads?limit=100&offset=0`
List all leads (paginated)

### `GET /api/models`
List available Ollama models (only when `AI_BACKEND=ollama`)

### `GET /health`
Health check endpoint - verifies database, AI service, and Telegram connectivity

## Testing

### Run Unit Tests
```bash
pytest -v
```

### Test with curl
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

### Test with Swagger UI
Navigate to http://localhost:8000/docs and use the interactive interface

## Example Usage

1. **Submit a test lead:**
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@startup.io",
    "phone": "+1-555-999-8888",
    "company": "Startup Inc",
    "message": "Looking for a demo next week. Budget approved."
  }'
```

2. **Check the database:**
```bash
sqlite3 leads.db "SELECT id, name, email, temperature, priority_score FROM leads;"
```

3. **Verify Telegram notification** was received in your configured chat

4. **Retrieve the lead:**
```bash
curl http://localhost:8000/api/leads/1
```

## Data Normalization

The system automatically normalizes incoming data:
- **Email**: Lowercased, trimmed
- **Phone**: Non-digit characters removed (except '+')
- **Name/Company**: Title-cased, trimmed
- **Message**: Trimmed

Original raw JSON is preserved for audit purposes.

## AI Classification Logic

Leads are classified based on:
- **Hot**: Immediate opportunity with clear need and urgency
- **Warm**: Interested but not urgent, needs nurturing
- **Cold**: Low quality, vague, or not qualified

Priority score (0-100) indicates urgency and potential value.

## Project Structure

```
LandingScratch/
├── main.py                 # FastAPI application
├── config.py               # Configuration loader
├── models.py               # Pydantic models
├── database.py             # SQLite operations
├── ai_service.py           # AI service implementations
├── telegram_notifier.py    # Telegram integration
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── .env                    # Your secrets (gitignored)
├── test_payload.json       # Example lead data
├── README.md               # This file
├── tests/                  # Unit tests
└── leads.db                # SQLite database (created on first run)
```

## Troubleshooting

**Ollama connection issues:**
- Verify Ollama is running: `ollama list`
- Check the base URL: `curl http://localhost:11434/api/tags`

**Telegram not sending:**
- Verify bot token: Check for typos in `.env`
- Verify chat ID: Make sure it's correct format (numbers only)
- Check bot permissions if using a channel

**Database errors:**
- Ensure write permissions in the project directory
- Delete `leads.db` to recreate the schema

**Import errors:**
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Future Enhancements

For production deployment, consider:
- Authentication/API keys for endpoints
- Rate limiting
- Async queue for AI processing (Celery/RQ)
- PostgreSQL for better concurrency
- Docker containerization
- Monitoring and observability (Prometheus, Grafana)
- Email notifications alongside Telegram
- CRM integration (Salesforce, HubSpot)
- Webhook support for landing page platforms
- Lead deduplication logic
- Advanced analytics dashboard

## Development

**Running in development mode:**
```bash
uvicorn main:app --reload --log-level debug
```

**Testing AI service directly:**
```python
from config import Config
from ai_service import get_ai_service
import asyncio

config = Config.load()
ai = get_ai_service(config)

async def test():
    summary = await ai.generate_summary({"name": "Test", "message": "Demo"})
    print(summary)

asyncio.run(test())
```

## License

MIT License - This is an MVP for demonstration purposes.

## Support

For issues or questions, refer to the code comments or check:
- FastAPI docs: https://fastapi.tiangolo.com/
- Ollama docs: https://ollama.ai/
- python-telegram-bot docs: https://python-telegram-bot.org/
