import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


# Auth
class LoginRequest(BaseModel):
    password: str


class MeResponse(BaseModel):
    sub: str


# Sources
class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: Literal["resume", "url"]
    label: str
    url: Optional[str]
    status: Literal["ready", "failed"]
    error: Optional[str]
    chunk_count: int
    indexed_at: Optional[datetime]
    created_at: datetime


# Ingest
class IngestUrlRequest(BaseModel):
    url: HttpUrl
    label: str = Field(..., min_length=1, max_length=100)


class GitHubRequest(BaseModel):
    query: Optional[str] = None


class AppointmentRequest(BaseModel):
    visitor_name: str = Field(..., min_length=1, max_length=120)
    visitor_email: EmailStr
    start_time: str = Field(..., description="ISO 8601 UTC datetime, e.g. 2026-07-12T06:30:00Z")
    timezone: str = Field(default="Asia/Kolkata", description="Visitor's timezone, e.g. America/New_York")
    notes: str = Field(default="", max_length=1000)


class SlotCheckRequest(BaseModel):
    date: str = Field(..., description="Target date, YYYY-MM-DD format")
    timezone: str = Field(default="Asia/Kolkata", description="Visitor's timezone")


class ContactMessageRequest(BaseModel):
    visitor_name: str = Field(..., min_length=1, max_length=120)
    visitor_email: EmailStr
    message: str = Field(..., min_length=1, max_length=5000)


class ContactMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    visitor_name: str
    visitor_email: str
    message: str
    created_at: datetime

