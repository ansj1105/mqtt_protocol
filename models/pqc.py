"""
Post-Quantum Cryptography domain models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class PQCAlgorithmType(str, Enum):
    """PQC algorithm types."""
    KYBER512 = "kyber512"
    KYBER768 = "kyber768"
    KYBER1024 = "kyber1024"
    KYBER768_X25519 = "kyber768_x25519"  # Hybrid
    KYBER1024_X448 = "kyber1024_x448"    # Hybrid


class PQCSessionStatus(str, Enum):
    """PQC session status."""
    INITIATED = "initiated"
    HANDSHAKE_IN_PROGRESS = "handshake_in_progress"
    ESTABLISHED = "established"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class PQCSession:
    """Domain model for PQC session."""
    
    id: str
    connection_id: str
    algorithm: PQCAlgorithmType
    status: PQCSessionStatus = PQCSessionStatus.INITIATED
    created_at: datetime = field(default_factory=datetime.utcnow)
    established_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Keys (in production, these would be secure byte arrays)
    client_public_key: Optional[str] = None
    server_public_key: Optional[str] = None
    shared_secret_hash: Optional[str] = None  # Hash only, not actual secret
    
    def is_hybrid(self) -> bool:
        """Check if using hybrid algorithm."""
        return "_" in self.algorithm.value
    
    def establish(self, ttl_seconds: int = 3600):
        """Mark session as established."""
        self.status = PQCSessionStatus.ESTABLISHED
        self.established_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
    
    def is_valid(self) -> bool:
        """Check if session is valid."""
        if self.status != PQCSessionStatus.ESTABLISHED:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            self.status = PQCSessionStatus.EXPIRED
            return False
        return True
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "algorithm": self.algorithm.value,
            "status": self.status.value,
            "is_hybrid": self.is_hybrid(),
            "created_at": self.created_at.isoformat(),
            "established_at": self.established_at.isoformat() if self.established_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "is_valid": self.is_valid(),
        }

