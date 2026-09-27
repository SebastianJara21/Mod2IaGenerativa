"""Habito request/response schemas (validation contracts)."""

from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class HabitoCreate(BaseModel):
    """Request schema for creating a habit."""
    nombre: str = Field(..., min_length=1, max_length=255)
    frecuencia_objetivo: int = Field(..., ge=1, le=7, description="Target frequency: 1-7 per week")


class HabitoResponse(BaseModel):
    """Response schema for habit."""
    id: int
    usuario_id: int
    nombre: str
    frecuencia_objetivo: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MarcaCreate(BaseModel):
    """Request schema for marking a habit completed."""
    fecha: date = Field(..., description="Date to mark (must not be future)")


class MarcaResponse(BaseModel):
    """Response schema for habit completion mark."""
    id: int
    habito_id: int
    usuario_id: int
    fecha: date

    model_config = ConfigDict(from_attributes=True)
