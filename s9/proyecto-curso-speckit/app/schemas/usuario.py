"""Pydantic schemas for user registration and authentication.

Per Artículo V (REST Design): Separate input/output schemas.
UsuarioCreate: What client sends (email, password)
UsuarioOut: What server returns (id, email, created_at — NO password)
Per Artículo IV (Security): password never exposed in responses.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UsuarioCreate(BaseModel):
    """User registration request schema.

    Requires:
    - email: valid RFC 5321 email (validated by EmailStr)
    - password: non-empty string (at minimum — no length constraint specified)
    """
    email: EmailStr
    password: str = Field(..., min_length=1, description="User password, never stored in plain text")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "password": "mi_contraseña_segura"
            }
        }


class UsuarioOut(BaseModel):
    """User registration response schema.

    Returns basic user info WITHOUT password.
    Per Artículo IV.5: Passwords NEVER exposed in API responses.
    """
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "usuario@example.com",
                "created_at": "2026-09-23T12:00:00Z"
            }
        }
