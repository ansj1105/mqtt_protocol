"""
PQC schemas for validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PQCHandshakeRequestSchema(BaseModel):
    """Schema for PQC handshake request."""
    algorithm: str
    public_key: str
    client_info: Optional[dict] = None


class PQCHandshakeResponseSchema(BaseModel):
    """Schema for PQC handshake response."""
    success: bool
    algorithm: str
    server_public_key: Optional[str] = None
    session_id: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PQCSessionSchema(BaseModel):
    """Schema for PQC session."""
    id: str
    connection_id: str
    algorithm: str
    status: str
    is_hybrid: bool
    created_at: datetime
    established_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_valid: bool
    
    class Config:
        from_attributes = True


class PQCInfoSchema(BaseModel):
    """Schema for PQC information."""
    enabled: bool
    algorithms: dict
    supported_algorithms: list
    description: str

