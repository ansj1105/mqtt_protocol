"""
TC375 schemas for validation.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class TC375DeviceSchema(BaseModel):
    """Schema for TC375 device."""
    id: str
    connection_id: str
    protocol: str
    status: str
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    registered_at: datetime
    last_heartbeat: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class TC375CommandSchema(BaseModel):
    """Schema for TC375 command."""
    command_type: str
    device_id: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=30, ge=1, le=300)
    retries: int = Field(default=3, ge=0, le=10)


class TC375ResponseSchema(BaseModel):
    """Schema for TC375 response."""
    command_type: str
    device_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: Optional[float] = None
    received_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class TC375StatusSchema(BaseModel):
    """Schema for TC375 status response."""
    tc375_devices: int
    devices: List[TC375DeviceSchema]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

