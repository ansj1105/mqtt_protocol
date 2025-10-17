"""
Message domain model.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
import uuid


class MessageType(str, Enum):
    """Message type enumeration."""
    PING = "ping"
    PONG = "pong"
    WELCOME = "welcome"
    ERROR = "error"
    COMMAND = "command"
    COMMAND_RESPONSE = "command_response"
    PQC_HANDSHAKE = "pqc_handshake"
    PQC_HANDSHAKE_RESPONSE = "pqc_handshake_response"
    TC375_DATA = "tc375_data"
    TC375_DATA_RESPONSE = "tc375_data_response"
    TC375_COMMAND = "tc375_command"
    STATUS = "status"
    STATUS_RESPONSE = "status_response"
    BROADCAST = "broadcast"
    MESSAGE = "message"


@dataclass
class Message:
    """Domain model for a message."""
    
    type: MessageType
    payload: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    connection_id: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], connection_id: Optional[str] = None) -> "Message":
        """Create message from dictionary."""
        return cls(
            type=MessageType(data.get("type")),
            payload=data.get("payload", {}),
            id=data.get("id", str(uuid.uuid4())),
            correlation_id=data.get("correlation_id"),
            connection_id=connection_id,
        )

