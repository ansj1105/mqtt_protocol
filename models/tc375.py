"""
TC375 Litekit domain models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class TC375Protocol(str, Enum):
    """TC375 protocol version."""
    V1 = "v1"
    V2 = "v2"


class TC375CommandType(str, Enum):
    """TC375 command types."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    QUERY = "query"
    CONFIG = "config"


class TC375Status(str, Enum):
    """TC375 device status."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


@dataclass
class TC375Device:
    """Domain model for TC375 Litekit device."""
    
    id: str
    connection_id: str
    protocol: TC375Protocol = TC375Protocol.V2
    status: TC375Status = TC375Status.ONLINE
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None
    registered_at: datetime = field(default_factory=datetime.utcnow)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_heartbeat(self):
        """Update last heartbeat timestamp."""
        self.last_heartbeat = datetime.utcnow()
        if self.status == TC375Status.OFFLINE:
            self.status = TC375Status.ONLINE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "protocol": self.protocol.value,
            "status": self.status.value,
            "firmware_version": self.firmware_version,
            "hardware_version": self.hardware_version,
            "registered_at": self.registered_at.isoformat(),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class TC375Command:
    """Domain model for TC375 command."""
    
    command_type: TC375CommandType
    device_id: str
    parameters: Dict[str, Any]
    timeout: int = 30
    retries: int = 3
    issued_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command_type": self.command_type.value,
            "device_id": self.device_id,
            "parameters": self.parameters,
            "timeout": self.timeout,
            "issued_at": self.issued_at.isoformat(),
        }


@dataclass
class TC375Response:
    """Domain model for TC375 response."""
    
    command_type: TC375CommandType
    device_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: Optional[float] = None
    received_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command_type": self.command_type.value,
            "device_id": self.device_id,
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "received_at": self.received_at.isoformat(),
        }

