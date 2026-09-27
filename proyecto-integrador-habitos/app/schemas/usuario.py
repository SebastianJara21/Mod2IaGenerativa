"""Pydantic schemas for usuario input/output (separate from ORM models)."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UsuarioCreate(BaseModel):
    """User registration input (FR-001)."""
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")


class UsuarioResponse(BaseModel):
    """User response (FR-020: password NEVER exposed)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    created_at: datetime


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
