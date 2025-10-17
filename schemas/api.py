"""
API schemas for REST endpoints.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class BroadcastRequestSchema(BaseModel):
    """Schema for broadcast request."""
    message: Dict[str, Any]
    exclude: Optional[list] = Field(default_factory=list)


class SendMessageRequestSchema(BaseModel):
    """Schema for send message request."""
    client_id: str
    message: Dict[str, Any]


class DisconnectRequestSchema(BaseModel):
    """Schema for disconnect request."""
    client_id: str
    reason: Optional[str] = None


class HealthResponseSchema(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusResponseSchema(BaseModel):
    """Schema for status response."""
    status: str
    active_connections: int
    max_connections: int
    uptime: Optional[str] = None
    tls_enabled: bool
    pqc_enabled: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponseSchema(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponseSchema(BaseModel):
    """Schema for success response."""
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

