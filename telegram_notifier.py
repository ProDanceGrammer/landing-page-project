import logging
from telegram import Bot
from telegram.error import TelegramError
from models import LeadClassification
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def send_lead_notification(
    lead_id: int,
    lead_data: dict,
    ai_summary: str,
    classification: LeadClassification,
    config: Config
):
    try:
        bot = Bot(token=config.TELEGRAM_BOT_TOKEN)

        message = f"""🎯 New Lead #{lead_id}

📋 Contact:
Name: {lead_data.get('name', 'N/A')}
Email: {lead_data.get('email', 'N/A')}
Company: {lead_data.get('company', 'N/A')}

📝 Summary: {ai_summary}

🔥 Classification: {classification.temperature} | Priority: {classification.priority_score}/100
💡 Reasoning: {classification.reasoning}
"""

        await bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=message
        )

        logger.info(f"Telegram notification sent for lead #{lead_id}")

    except TelegramError as e:
        logger.error(f"Telegram error sending notification for lead #{lead_id}: {e}")
    except Exception as e:
        logger.error(f"Error sending notification for lead #{lead_id}: {e}")
