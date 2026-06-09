import os
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    AI_BACKEND: Literal["ollama", "openai"]
    OLLAMA_MODEL: str
    OLLAMA_BASE_URL: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str
    DATABASE_PATH: str
    PHONE_NUMBER: str
    LINKEDIN_URL: str
    GITHUB_URL: str
    RESUME_URL: str

    @classmethod
    def load(cls) -> "Config":
        ai_backend = os.getenv("AI_BACKEND", "ollama")

        if ai_backend not in ["ollama", "openai"]:
            raise ValueError(f"Invalid AI_BACKEND: {ai_backend}. Must be 'ollama' or 'openai'")

        config = cls(
            AI_BACKEND=ai_backend,
            OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "llama3"),
            OLLAMA_BASE_URL=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
            OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID", ""),
            DATABASE_PATH=os.getenv("DATABASE_PATH", "leads.db"),
            PHONE_NUMBER=os.getenv("PHONE_NUMBER", ""),
            LINKEDIN_URL=os.getenv("LINKEDIN_URL", ""),
            GITHUB_URL=os.getenv("GITHUB_URL", ""),
            RESUME_URL=os.getenv("RESUME_URL", ""),
        )

        config._validate()
        return config

    def _validate(self):
        if self.AI_BACKEND == "openai" and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when AI_BACKEND=openai")

        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

        if not self.TELEGRAM_CHAT_ID:
            raise ValueError("TELEGRAM_CHAT_ID is required")
