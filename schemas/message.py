"""
Message schemas for validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MessageCreateSchema(BaseModel):
    """Schema for creating a message."""
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None


class MessageSchema(BaseModel):
    """Schema for message response."""
    id: str
    type: str
    payload: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    
    class Config:
        from_attributes = True

