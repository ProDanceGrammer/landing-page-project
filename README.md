# Lead Processing MVP with Landing Page

A complete FastAPI-based system for processing lead applications with an optimized landing page, AI-powered summarization, and real-time classification.

**🌐 Live Demo**: https://vasyl-yarmolenko.online

## Features

- 🎨 **Optimized Landing Page** - Single-page portfolio with animated hero, project showcase, and contact form
- 🚀 **REST API** - Async backend for receiving and processing lead applications
- 🤖 **Pluggable AI backends** - Ollama (local) or OpenAI (cloud) for lead intelligence
- 📊 **Automatic lead classification** - Hot/Warm/Cold with priority scoring (0-100)
- 💾 **PostgreSQL database** - Production-ready with Neon serverless
- 📱 **Telegram notifications** - Real-time alerts for new leads
- ⚡ **Background processing** - Immediate response + async AI analysis
- ✅ **Input validation** - Pydantic models with email validation
- 🧪 **Unit tests** - 23 tests with pytest
- 📖 **API documentation** - Auto-generated Swagger/OpenAPI
- 🔄 **CI/CD Pipeline** - Automated deployment with GitHub Actions
- 📡 **Monitoring** - Keep-warm strategy to prevent cold starts

## Production Architecture

```
Frontend (Vercel)                Backend (Render)              Database (Neon)
vasyl-yarmolenko.online    →    landing-backend.onrender.com  →  PostgreSQL
     ↓                                    ↓
Static Landing Page              FastAPI + Ollama + OpenAI
     ↓                                    ↓
Contact Form Submit         →    AI Classification + Telegram
                                         ↓
                            Monitoring (UptimeRobot + GitHub Actions)
```

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/ProDanceGrammer/landing-page-project.git
cd landing-page-project

# Activate virtual environment
source .venv/Scripts/activate  # Windows Git Bash

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run locally
uvicorn main:app --reload

# Access
# - Landing page: http://localhost:8000
# - API docs: http://localhost:8000/docs
```

### Production Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete deployment guide including:
- Neon PostgreSQL setup
- Render backend deployment
- Vercel frontend deployment
- GitHub Actions CI/CD
- Monitoring configuration

**Deployment is 100% free** using free tiers of Vercel, Render, and Neon.

## Architecture

```
Landing Page (static/index.html) → Contact Form → POST /api/leads
                                                        ↓
                                    Validation & Normalization (Pydantic)
                                                        ↓
                                Save to DB (status: "received") → Immediate Response
                                                        ↓
                                Background Task (asyncio.create_task):
                                    - AI Summary Generation
                                    - Lead Classification (Hot/Warm/Cold)
                                    - Update DB (status: "processed")
                                    - Send Telegram Notification
```

**Key Components:**
- **static/index.html**: Optimized single-page portfolio (minified CSS/JS, 13KB)
- **main.py**: FastAPI app with async background processing pattern
- **config.py**: Environment-based configuration loader
- **models.py**: Pydantic models for request/response validation
- **database.py**: SQLite operations and data normalization
- **ai_service.py**: Pluggable AI service (Ollama/OpenAI) with strategy pattern
- **telegram_notifier.py**: Telegram Bot API integration

**Performance Optimizations:**
- Async background processing for AI tasks (immediate response)
- Minified CSS/JS in landing page
- Intersection Observer API for lazy animations
- Optimized gradient animations with GPU acceleration

## Prerequisites

- **Python 3.10+**
- **Ollama** (if using local AI): [Download here](https://ollama.ai/)
- **Telegram Bot Token**: Create via [@BotFather](https://t.me/botfather)

## Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source .venv/Scripts/activate  # Windows Git Bash
# or
.venv\Scripts\activate  # Windows CMD

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `.env` with your actual credentials:
```env
AI_BACKEND=ollama
OLLAMA_MODEL=llama3
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

### 2. Start Services

**If using Ollama (Local AI):**
```bash
# In a separate terminal
ollama serve

# Pull a model if needed
ollama pull llama3
```

**Start the FastAPI server:**
```bash
uvicorn main:app --reload
```

### 3. Access the Application

- **Landing Page**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

The landing page includes:
- Animated hero section with profile
- Project showcase with metrics
- Core expertise cards
- Contact form (submits to `/api/leads`)

### 4. Test the System

**Submit a test lead via curl:**
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Or use the landing page contact form** at http://localhost:8000

**Check the database:**
```bash
sqlite3 leads.db "SELECT id, name, email, temperature, priority_score, status FROM leads;"
```

## Configuration

### AI Backend Options

**Option 1: Ollama (Local - Recommended for Development)**
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

### Landing Page Customization

Edit `static/index.html` to customize:
- Profile photo: Replace `/static/images/profile.jpg`
- Personal info: Update hero section content
- Projects: Modify project cards with your own work
- Social links: Update LinkedIn, GitHub, email in footer
- Resume link: Update Google Docs link in navbar

The page uses inline CSS/JS for performance (single file, no external dependencies).

## Running the Application

### Development Mode

```bash
# Start Ollama (if using local AI)
ollama serve  # in separate terminal

# Run FastAPI with auto-reload
uvicorn main:app --reload

# With debug logging
uvicorn main:app --reload --log-level debug

# Custom host/port
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Production Considerations

```bash
# Run with Gunicorn (for production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Uvicorn with workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Accessing the Application

- **Landing Page**: http://localhost:8000 (static/index.html)
- **API Root**: http://localhost:8000/api
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Background Processing Flow

1. User submits form on landing page
2. API receives POST to `/api/leads` → validates data
3. Lead saved immediately with status "received"
4. API returns 201 response instantly
5. Background task spawns (`asyncio.create_task`):
   - Generates AI summary
   - Classifies lead (Hot/Warm/Cold + priority score)
   - Updates database with status "processed"
   - Sends Telegram notification

This ensures the landing page contact form responds quickly while AI processing happens asynchronously.

## API Endpoints

### Landing Page
- `GET /` - Serves the optimized landing page (static/index.html)
- `GET /static/*` - Static assets (images, if any)

### Lead Management

#### `POST /api/leads`
Submit a new lead application (used by landing page contact form)

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

**Response (201 Created):**
```json
{
  "id": 1,
  "received_at": "2026-06-10T11:00:00",
  "normalized_data": {
    "name": "John Smith",
    "email": "john.smith@techcorp.com",
    "phone": "+15551234567",
    "company": "Techcorp Inc",
    "message": "We're interested in your enterprise solution..."
  },
  "ai_summary": "Your message has been received and is being processed.",
  "classification": {
    "temperature": "Warm",
    "priority_score": 50,
    "reasoning": "Processing in background"
  },
  "status": "received"
}
```

Note: The lead is saved immediately with status "received". Background processing updates it to "processed" with full AI analysis.

#### `GET /api/leads/{lead_id}`
Retrieve a specific lead by ID (with full AI analysis if completed)

#### `GET /api/leads?limit=100&offset=0`
List all leads (paginated, max 500 per request)

### Monitoring

#### `GET /health`
Health check endpoint - verifies connectivity to:
- Database (SQLite)
- AI service (Ollama or OpenAI)
- Telegram bot

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-06-10T11:00:00",
  "checks": {
    "database": "ok",
    "ai_service": "ok",
    "telegram": "ok"
  }
}
```

#### `GET /api/models`
List available Ollama models (only when `AI_BACKEND=ollama`)

#### `GET /api`
API root with version info

## Testing

### Run Unit Tests
```bash
# All tests with verbose output
pytest -v

# Specific test file
pytest tests/test_api.py -v

# Specific test by name
pytest -k test_create_lead

# With coverage report
pytest --cov=. --cov-report=html
```

**Test Coverage**: 23 tests across 3 test suites
- `tests/test_api.py` - 9 tests (endpoints, validation, error handling)
- `tests/test_database.py` - 6 tests (CRUD operations, normalization)
- `tests/test_ai_service.py` - 8 tests (Ollama, OpenAI, fallbacks)

### Test with curl

**Submit a lead:**
```bash
curl -X POST http://localhost:8000/api/leads \
  -H "Content-Type: application/json" \
  -d @test_payload.json
```

**Check health:**
```bash
curl http://localhost:8000/health | jq
```

**Get all leads:**
```bash
curl http://localhost:8000/api/leads | jq
```

**Get specific lead:**
```bash
curl http://localhost:8000/api/leads/1 | jq
```

### Test with Browser

1. **Landing Page**: Open http://localhost:8000
   - Test smooth scrolling navigation
   - Test animations (fade-in on scroll)
   - Fill and submit contact form
   - Verify success message appears

2. **API Docs**: Open http://localhost:8000/docs
   - Test endpoints interactively
   - View request/response schemas

### Test Database

```bash
# View all leads
sqlite3 leads.db "SELECT * FROM leads;"

# View summary
sqlite3 leads.db "SELECT id, name, email, temperature, priority_score, status FROM leads;"

# Count leads by temperature
sqlite3 leads.db "SELECT temperature, COUNT(*) FROM leads GROUP BY temperature;"
```

## Example Usage

### Complete Workflow

1. **Start the application:**
```bash
# Terminal 1: Start Ollama (if using local AI)
ollama serve

# Terminal 2: Start FastAPI
source .venv/Scripts/activate
uvicorn main:app --reload
```

2. **Open the landing page:**
   - Navigate to http://localhost:8000
   - Scroll through the portfolio sections
   - Fill out the contact form at the bottom

3. **Submit a lead via the landing page:**
   - Name: Jane Doe
   - Email: jane@startup.io
   - Phone: +1-555-999-8888
   - Company: Startup Inc
   - Message: "Looking for a demo next week. Budget approved."
   - Click "Send Message"

4. **What happens next:**
   - Immediate response: "Thank you! I have received your message and will respond soon."
   - Lead saved to database with status "received"
   - Background task processes:
     - AI generates summary
     - AI classifies as Hot/Warm/Cold with priority score
     - Database updated to status "processed"
     - Telegram notification sent

5. **Check results:**
```bash
# View in database
sqlite3 leads.db "SELECT id, name, email, temperature, priority_score FROM leads;"

# Retrieve via API
curl http://localhost:8000/api/leads/1 | jq

# Check Telegram for notification
```

### Alternative: Submit via API

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

## Landing Page Features

### Design & Performance
- **Single-file optimization**: All CSS/JS inline (no external dependencies)
- **Minified assets**: ~13KB total page size
- **GPU-accelerated animations**: Smooth gradient shifts and floating elements
- **Responsive design**: Mobile-first with breakpoints
- **Lazy animations**: Intersection Observer API for scroll-triggered fade-ins
- **Fast form submission**: Async fetch with immediate feedback

### Sections
1. **Hero**: Animated gradient background, profile photo with float animation, CTA buttons
2. **Stats**: 4 metric cards with hover effects
3. **Expertise**: Core technical skills in card layout
4. **Projects**: Featured work with metrics and tech tags
5. **Contact Form**: Integrated with `/api/leads` endpoint
6. **Footer**: Social links and contact information

### Customization Guide

**Update Profile Information** (`static/index.html`):
- Line 6: Update `<title>` tag
- Line 14: Profile photo path
- Line 14-16: Hero text (name, title, description)
- Line 13: Resume link in navbar

**Modify Projects**:
- Lines 17: Project cards with metrics and tech tags
- Add/remove projects by duplicating/removing `.project-card` divs

**Change Colors**:
- Line 9: CSS variables in `:root` selector
- `--primary`: Gradient colors (currently purple)
- `--success`, `--dark`, `--light`: UI colors

**Social Links**:
- Line 19: Footer social links (LinkedIn, GitHub, Email)

### Form Integration

The contact form posts to `/api/leads`:
```javascript
fetch("/api/leads", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify(formData)
})
```

Success shows: "Thank you! I have received your message and will respond soon."
Error shows: "Sorry, there was an error. Please try again or email me directly."

## Data Processing

### Data Normalization
The system automatically normalizes incoming data before storage:
- **Email**: Lowercased, trimmed (`john.smith@techcorp.com`)
- **Phone**: Non-digit characters removed except '+' (`+15551234567`)
- **Name/Company**: Title-cased, trimmed (`John Smith`, `Techcorp Inc`)
- **Message**: Trimmed

Original raw JSON is preserved in the database for audit purposes.

### AI Classification Logic

**Lead Temperature:**
- **Hot**: Immediate opportunity with clear need and urgency (e.g., "budget approved", "need demo next week")
- **Warm**: Interested but not urgent, needs nurturing (e.g., "exploring options")
- **Cold**: Low quality, vague, or not qualified (e.g., "just looking")

**Priority Score**: 0-100 scale indicating urgency and potential value
- 80-100: High priority (immediate follow-up)
- 50-79: Medium priority (follow-up within 24-48h)
- 0-49: Low priority (nurture campaign)

**Classification includes reasoning**: AI explains why it assigned the specific temperature and score.

### Background Processing Pattern

```python
# Immediate response pattern (main.py:176-211)
@app.post("/api/leads", response_model=LeadApplicationResponse, status_code=201)
async def create_lead(lead: LeadApplicationRequest):
    # 1. Save immediately with pending status
    lead_id = save_lead(..., status="received")
    
    # 2. Queue background task (non-blocking)
    asyncio.create_task(process_lead_async(lead_id, ...))
    
    # 3. Return immediate response
    return LeadApplicationResponse(status="received", ...)

# Background task processes AI analysis
async def process_lead_async(lead_id, ...):
    summary = await ai_service.generate_summary(...)
    classification = await ai_service.classify_lead(...)
    update_database(lead_id, status="processed", ...)
    await send_telegram_notification(...)
```

This pattern ensures:
- Fast user experience (<100ms response)
- AI processing doesn't block the form submission
- Graceful degradation if AI service is slow or unavailable

## Project Structure

```
LandingScratch/
├── static/
│   ├── index.html           # Optimized landing page (13KB, inline CSS/JS)
│   └── images/
│       └── profile.jpg      # Profile photo for hero section
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API endpoint tests (9 tests)
│   ├── test_database.py     # Database operation tests (6 tests)
│   └── test_ai_service.py   # AI service tests (8 tests)
├── main.py                  # FastAPI application with async background processing
├── config.py                # Environment-based configuration loader
├── models.py                # Pydantic validation models
├── database.py              # SQLite operations and data normalization
├── ai_service.py            # Pluggable AI service (Ollama/OpenAI)
├── telegram_notifier.py     # Telegram Bot API integration
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .env                     # Your secrets (gitignored)
├── test_payload.json        # Example lead data for testing
├── pyproject.toml           # Pytest configuration
├── README.md                # This file
├── CLAUDE.md                # Claude Code guidance
└── leads.db                 # SQLite database (auto-created on first run)
```

## Troubleshooting

### Landing Page Issues

**Landing page not loading:**
- Verify FastAPI is running: `curl http://localhost:8000/health`
- Check static files directory exists: `ls -la static/`
- Ensure `index.html` exists in static folder
- Check browser console for JavaScript errors

**Form submission not working:**
- Open browser DevTools Network tab
- Submit form and check for POST to `/api/leads`
- Verify response is 201 (success) or check error message
- Test API directly: `curl -X POST http://localhost:8000/api/leads -H "Content-Type: application/json" -d @test_payload.json`

**Images not displaying:**
- Check image path: `/static/images/profile.jpg`
- Verify file exists: `ls -la static/images/`
- Check browser console for 404 errors

### API/Backend Issues

**Ollama connection issues:**
- Verify Ollama is running: `ollama list`
- Check connectivity: `curl http://localhost:11434/api/tags`
- Check logs: Look for "Ollama API error" in terminal
- Model auto-detection: OllamaService detects and uses available models at startup

**Telegram not sending:**
- Verify bot token in `.env` (no spaces, correct format)
- Verify chat ID in `.env` (numbers only)
- Test bot manually: Message your bot on Telegram
- Check logs for "Error sending Telegram notification"
- Telegram failures don't block API responses (graceful degradation)

**Database errors:**
- Ensure write permissions in project directory
- Delete and recreate: `rm leads.db` then restart app
- Check schema: `sqlite3 leads.db ".schema leads"`
- Verify data: `sqlite3 leads.db "SELECT * FROM leads LIMIT 5;"`

**Import errors:**
- Verify virtual environment is activated: `which python` should show `.venv`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

**AI processing slow or failing:**
- Check health endpoint: `curl http://localhost:8000/health`
- AI failures use fallback (Warm/50 priority)
- For Ollama: Ensure model is pulled (`ollama pull llama3`)
- For OpenAI: Verify API key in `.env`

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn main:app --port 8080
```

## Future Enhancements

### Production Deployment
- **Authentication**: API keys or JWT tokens for endpoint security
- **Rate limiting**: Prevent abuse with per-IP request limits
- **PostgreSQL**: Replace SQLite for better concurrency and production scale
- **Docker**: Containerize with docker-compose (app + Ollama + PostgreSQL)
- **HTTPS**: SSL/TLS certificates with Let's Encrypt
- **CDN**: Serve static assets via CloudFlare or similar

### Monitoring & Observability
- **Logging**: Structured logging with ELK stack or Grafana Loki
- **Metrics**: Prometheus + Grafana dashboards
- **APM**: Application performance monitoring with Sentry or New Relic
- **Uptime monitoring**: Health check pings with UptimeRobot or Pingdom

### Feature Enhancements
- **Email notifications**: Send emails alongside Telegram via SendGrid/AWS SES
- **Lead deduplication**: Detect and merge duplicate submissions
- **CRM integration**: Sync leads to Salesforce, HubSpot, or Pipedrive
- **Webhook support**: Push notifications to external systems
- **Admin dashboard**: Web UI for viewing/managing leads
- **A/B testing**: Test different landing page variants
- **Analytics**: Track conversion rates, form field drop-offs
- **Multi-language**: i18n support for landing page

### AI Improvements
- **Async queue**: Use Celery/RQ for background AI processing at scale
- **Fine-tuned models**: Train custom models on historical lead data
- **Lead scoring model**: ML model predicting conversion probability
- **Auto-response**: Generate personalized email responses based on lead type
- **Sentiment analysis**: Detect tone and urgency in messages

## Development Tips

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

**Debugging Telegram:**
```python
from telegram import Bot
from config import Config
import asyncio

config = Config.load()

async def test():
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
    me = await bot.get_me()
    print(f"Bot: {me.username}")
    await bot.send_message(chat_id=config.TELEGRAM_CHAT_ID, text="Test")

asyncio.run(test())
```

**Hot reload landing page changes:**
- Edit `static/index.html`
- Refresh browser (no server restart needed)
- For CSS/JS changes, hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

## License

MIT License - This is an MVP for demonstration purposes.

## Support

For issues or questions:
- Check this README and CLAUDE.md first
- Review FastAPI docs: https://fastapi.tiangolo.com/
- Review Ollama docs: https://ollama.ai/
- Review python-telegram-bot docs: https://python-telegram-bot.org/

## Contact

**Vasyl Yarmolenko**
- Email: prodancegrammer@gmail.com
- LinkedIn: https://www.linkedin.com/in/vasyl-yarmolenko/
- GitHub: https://github.com/ProDanceGrammer

---

**Last Updated**: 2026-06-10  
**Status**: Production-ready MVP with optimized landing page
