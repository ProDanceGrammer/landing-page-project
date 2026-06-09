from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


class LeadApplicationRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Full name of the lead")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")
    message: str = Field(..., min_length=1, description="Lead inquiry message")


class LeadClassification(BaseModel):
    temperature: Literal["Hot", "Warm", "Cold"]
    priority_score: int = Field(..., ge=0, le=100)
    reasoning: str


class LeadApplicationResponse(BaseModel):
    id: int
    received_at: datetime
    normalized_data: dict
    ai_summary: str
    classification: LeadClassification
    status: str
