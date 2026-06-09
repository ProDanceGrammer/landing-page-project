from abc import ABC, abstractmethod
import httpx
import json
import logging
from typing import Optional
from models import LeadClassification
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIService(ABC):
    @abstractmethod
    async def generate_summary(self, lead_data: dict) -> str:
        pass

    @abstractmethod
    async def classify_lead(self, lead_data: dict, summary: str) -> LeadClassification:
        pass


class OllamaService(AIService):
    def __init__(self, config: Config):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL
        self._detect_model()

    def _detect_model(self):
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]

                if models:
                    if self.model in models:
                        logger.info(f"Using configured Ollama model: {self.model}")
                    else:
                        self.model = models[0]
                        logger.info(f"Configured model not found. Using first available: {self.model}")
                else:
                    logger.warning("No Ollama models found. Using configured model name anyway.")
            else:
                logger.warning(f"Could not detect Ollama models. Using: {self.model}")
        except Exception as e:
            logger.warning(f"Error detecting Ollama models: {e}. Using: {self.model}")

    async def generate_summary(self, lead_data: dict) -> str:
        prompt = f"""You are analyzing a B2B lead application. Summarize the following inquiry in 2-3 sentences, focusing on: what they need, their company context, and urgency.

Lead details:
Name: {lead_data.get('name', 'N/A')}
Company: {lead_data.get('company', 'N/A')}
Message: {lead_data.get('message', 'N/A')}

Provide a concise summary:"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "AI summary unavailable").strip()
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return "AI summary unavailable"
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "AI summary unavailable"

    async def classify_lead(self, lead_data: dict, summary: str) -> LeadClassification:
        prompt = f"""You are a lead qualification expert. Based on the following B2B lead, classify it as Hot/Warm/Cold and assign a priority score (0-100).

Hot = immediate opportunity with clear need and urgency
Warm = interested but not urgent, needs nurturing
Cold = low quality, vague, or not qualified

Lead details:
Name: {lead_data.get('name', 'N/A')}
Company: {lead_data.get('company', 'N/A')}
Message: {lead_data.get('message', 'N/A')}
Summary: {summary}

Respond in JSON format:
{{
  "temperature": "Hot|Warm|Cold",
  "priority_score": 0-100,
  "reasoning": "brief explanation"
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    response_text = result.get("response", "").strip()

                    classification_data = self._parse_classification(response_text)
                    return LeadClassification(**classification_data)
                else:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return self._fallback_classification()
        except Exception as e:
            logger.error(f"Error classifying lead: {e}")
            return self._fallback_classification()

    def _parse_classification(self, response_text: str) -> dict:
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)

                return {
                    "temperature": data.get("temperature", "Warm"),
                    "priority_score": int(data.get("priority_score", 50)),
                    "reasoning": data.get("reasoning", "AI classification")
                }
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Error parsing classification: {e}")
            return {
                "temperature": "Warm",
                "priority_score": 50,
                "reasoning": "Unable to parse AI response"
            }

    def _fallback_classification(self) -> LeadClassification:
        return LeadClassification(
            temperature="Warm",
            priority_score=50,
            reasoning="AI unavailable - default classification"
        )


class OpenAIService(AIService):
    def __init__(self, config: Config):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL

    async def generate_summary(self, lead_data: dict) -> str:
        prompt = f"""You are analyzing a B2B lead application. Summarize the following inquiry in 2-3 sentences, focusing on: what they need, their company context, and urgency.

Lead details:
Name: {lead_data.get('name', 'N/A')}
Company: {lead_data.get('company', 'N/A')}
Message: {lead_data.get('message', 'N/A')}

Provide a concise summary:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary with OpenAI: {e}")
            return "AI summary unavailable"

    async def classify_lead(self, lead_data: dict, summary: str) -> LeadClassification:
        prompt = f"""You are a lead qualification expert. Based on the following B2B lead, classify it as Hot/Warm/Cold and assign a priority score (0-100).

Hot = immediate opportunity with clear need and urgency
Warm = interested but not urgent, needs nurturing
Cold = low quality, vague, or not qualified

Lead details:
Name: {lead_data.get('name', 'N/A')}
Company: {lead_data.get('company', 'N/A')}
Message: {lead_data.get('message', 'N/A')}
Summary: {summary}

Respond in JSON format:
{{
  "temperature": "Hot|Warm|Cold",
  "priority_score": 0-100,
  "reasoning": "brief explanation"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )

            response_text = response.choices[0].message.content.strip()
            classification_data = self._parse_classification(response_text)
            return LeadClassification(**classification_data)
        except Exception as e:
            logger.error(f"Error classifying lead with OpenAI: {e}")
            return LeadClassification(
                temperature="Warm",
                priority_score=50,
                reasoning="AI unavailable - default classification"
            )

    def _parse_classification(self, response_text: str) -> dict:
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)

                return {
                    "temperature": data.get("temperature", "Warm"),
                    "priority_score": int(data.get("priority_score", 50)),
                    "reasoning": data.get("reasoning", "AI classification")
                }
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            logger.error(f"Error parsing classification: {e}")
            return {
                "temperature": "Warm",
                "priority_score": 50,
                "reasoning": "Unable to parse AI response"
            }


def get_ai_service(config: Config) -> AIService:
    if config.AI_BACKEND == "ollama":
        return OllamaService(config)
    elif config.AI_BACKEND == "openai":
        return OpenAIService(config)
    else:
        raise ValueError(f"Unknown AI backend: {config.AI_BACKEND}")
