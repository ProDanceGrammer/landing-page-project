from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import logging
from datetime import datetime
from typing import List
import asyncio

from models import LeadApplicationRequest, LeadApplicationResponse, LeadClassification
from config import Config
from database import init_database, normalize_data, save_lead, get_lead, get_all_leads
from ai_service import get_ai_service
from telegram_notifier import send_lead_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lead Processing MVP",
    description="API for processing lead applications with AI summary and classification",
    version="1.0.0"
)

config = Config.load()
ai_service = get_ai_service(config)


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    init_database(config.DATABASE_PATH)
    logger.info("Database initialized")

    logger.info(f"AI Backend: {config.AI_BACKEND}")
    if config.AI_BACKEND == "ollama":
        logger.info(f"Ollama Model: {ai_service.model}")
        logger.info(f"Ollama URL: {config.OLLAMA_BASE_URL}")


@app.get("/")
async def serve_landing_page():
    return FileResponse("static/index.html")


@app.get("/api")
async def api_root():
    return {
        "message": "Lead Processing MVP API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "unknown",
            "ai_service": "unknown",
            "telegram": "unknown"
        }
    }

    try:
        get_all_leads(limit=1, db_path=config.DATABASE_PATH)
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    try:
        if config.AI_BACKEND == "ollama":
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags")
                if response.status_code == 200:
                    health_status["checks"]["ai_service"] = "ok"
                else:
                    health_status["checks"]["ai_service"] = f"status: {response.status_code}"
        else:
            health_status["checks"]["ai_service"] = "ok (OpenAI configured)"
    except Exception as e:
        health_status["checks"]["ai_service"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    try:
        from telegram import Bot
        bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
        await bot.get_me()
        health_status["checks"]["telegram"] = "ok"
    except Exception as e:
        health_status["checks"]["telegram"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status


@app.get("/api/models")
async def list_models():
    if config.AI_BACKEND != "ollama":
        raise HTTPException(
            status_code=400,
            detail="This endpoint is only available when AI_BACKEND=ollama"
        )

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{config.OLLAMA_BASE_URL}/api/tags")

            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                return {
                    "backend": "ollama",
                    "current_model": ai_service.model,
                    "available_models": models
                }
            else:
                raise HTTPException(
                    status_code=502,
                    detail=f"Ollama API returned status {response.status_code}"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to Ollama: {str(e)}"
        )


async def process_lead_async(lead_id: int, raw_data: dict, normalized_data: dict):
    """Background task to process lead with AI and send notifications"""
    try:
        logger.info(f"Background processing lead {lead_id}: {normalized_data.get('email')}")

        # Generate AI summary
        summary = await ai_service.generate_summary(normalized_data)
        logger.info(f"Generated summary for lead {lead_id}: {summary[:50]}...")

        # Classify lead
        classification = await ai_service.classify_lead(normalized_data, summary)
        logger.info(f"Classification for lead {lead_id}: {classification.temperature}, Priority: {classification.priority_score}")

        # Update lead in database with AI results
        import sqlite3
        conn = sqlite3.connect(config.DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE leads
            SET ai_summary = ?,
                temperature = ?,
                priority_score = ?,
                classification_reasoning = ?,
                status = 'processed'
            WHERE id = ?
        """, (summary, classification.temperature, classification.priority_score, classification.reasoning, lead_id))
        conn.commit()
        conn.close()

        # Send Telegram notification
        await send_lead_notification(
            lead_id=lead_id,
            lead_data=normalized_data,
            ai_summary=summary,
            classification=classification,
            config=config
        )

        logger.info(f"Completed background processing for lead {lead_id}")

    except Exception as e:
        logger.error(f"Error in background processing for lead {lead_id}: {e}")


@app.post("/api/leads", response_model=LeadApplicationResponse, status_code=201)
async def create_lead(lead: LeadApplicationRequest, background_tasks: BackgroundTasks):
    try:
        raw_data = lead.model_dump()
        normalized = normalize_data(raw_data)

        logger.info(f"Received new lead: {normalized.get('email')}")

        # Save lead immediately with pending status
        lead_id = save_lead(
            raw_data=raw_data,
            normalized_data=normalized,
            ai_summary="Processing...",
            temperature="Warm",
            priority_score=50,
            reasoning="Pending AI analysis",
            db_path=config.DATABASE_PATH
        )
        logger.info(f"Lead saved with ID: {lead_id}, queuing background processing")

        # Queue background processing
        background_tasks.add_task(process_lead_async, lead_id, raw_data, normalized)

        # Return immediate response
        return LeadApplicationResponse(
            id=lead_id,
            received_at=datetime.utcnow(),
            normalized_data=normalized,
            ai_summary="Your message has been received and is being processed.",
            classification=LeadClassification(
                temperature="Warm",
                priority_score=50,
                reasoning="Processing in background"
            ),
            status="received"
        )

    except Exception as e:
        logger.error(f"Error receiving lead: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing lead: {str(e)}")


@app.get("/api/leads/{lead_id}", response_model=LeadApplicationResponse)
async def get_lead_by_id(lead_id: int):
    lead_record = get_lead(lead_id, config.DATABASE_PATH)

    if not lead_record:
        raise HTTPException(status_code=404, detail=f"Lead with ID {lead_id} not found")

    import json
    raw_json = json.loads(lead_record["raw_json"])
    normalized = normalize_data(raw_json)

    classification = LeadClassification(
        temperature=lead_record["temperature"],
        priority_score=lead_record["priority_score"],
        reasoning=lead_record["classification_reasoning"]
    )

    return LeadApplicationResponse(
        id=lead_record["id"],
        received_at=datetime.fromisoformat(lead_record["received_at"]),
        normalized_data=normalized,
        ai_summary=lead_record["ai_summary"],
        classification=classification,
        status=lead_record["status"]
    )


@app.get("/api/leads", response_model=List[LeadApplicationResponse])
async def list_leads(limit: int = 100, offset: int = 0):
    if limit > 500:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 500")

    lead_records = get_all_leads(limit=limit, offset=offset, db_path=config.DATABASE_PATH)

    results = []
    for lead_record in lead_records:
        import json
        raw_json = json.loads(lead_record["raw_json"])
        normalized = normalize_data(raw_json)

        classification = LeadClassification(
            temperature=lead_record["temperature"],
            priority_score=lead_record["priority_score"],
            reasoning=lead_record["classification_reasoning"]
        )

        results.append(LeadApplicationResponse(
            id=lead_record["id"],
            received_at=datetime.fromisoformat(lead_record["received_at"]),
            normalized_data=normalized,
            ai_summary=lead_record["ai_summary"],
            classification=classification,
            status=lead_record["status"]
        ))

    return results


# Mount static files AFTER all route definitions
app.mount("/static", StaticFiles(directory="static"), name="static")
