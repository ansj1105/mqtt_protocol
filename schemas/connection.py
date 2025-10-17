"""
Connection schemas for validation.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ConnectionCreateSchema(BaseModel):
    """Schema for creating a connection."""
    remote_address: tuple
    user_agent: Optional[str] = None
    protocol_version: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConnectionSchema(BaseModel):
    """Schema for connection response."""
    id: str
    remote_address: str
    status: str
    connected_at: datetime
    last_activity: datetime
    disconnected_at: Optional[datetime] = None
    messages_sent: int
    messages_received: int
    bytes_sent: int
    bytes_received: int
    protocol_version: Optional[str] = None
    pqc_session_id: Optional[str] = None
    tc375_device_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class ConnectionListSchema(BaseModel):
    """Schema for list of connections."""
    count: int
    connections: List[ConnectionSchema]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

