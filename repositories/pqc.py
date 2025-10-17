"""
PQC session repository.
"""

from typing import List, Optional
from datetime import datetime
from models.pqc import PQCSession, PQCSessionStatus, PQCAlgorithmType
from .base import BaseRepository


class PQCSessionRepository(BaseRepository[PQCSession]):
    """Repository for managing PQC sessions."""
    
    def get_by_connection(self, connection_id: str) -> Optional[PQCSession]:
        """Get active session by connection ID."""
        results = self.find_by(connection_id=connection_id)
        # Return the most recent established session
        valid_sessions = [s for s in results if s.is_valid()]
        return valid_sessions[0] if valid_sessions else None
    
    def get_by_algorithm(self, algorithm: PQCAlgorithmType) -> List[PQCSession]:
        """Get sessions by algorithm."""
        return self.find_by(algorithm=algorithm)
    
    def get_established_sessions(self) -> List[PQCSession]:
        """Get all established sessions."""
        return [s for s in self._storage.values() if s.status == PQCSessionStatus.ESTABLISHED]
    
    def get_valid_sessions(self) -> List[PQCSession]:
        """Get all valid (established and not expired) sessions."""
        return [s for s in self._storage.values() if s.is_valid()]
    
    def get_expired_sessions(self) -> List[PQCSession]:
        """Get all expired sessions."""
        return [
            s for s in self._storage.values()
            if s.expires_at and datetime.utcnow() > s.expires_at
        ]
    
    def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        expired = self.get_expired_sessions()
        for session in expired:
            session.status = PQCSessionStatus.EXPIRED
            self.update(session.id, session)
        return len(expired)
    
    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Delete old sessions."""
        to_delete = []
        cutoff = datetime.utcnow()
        
        for session_id, session in self._storage.items():
            if session.expires_at and (cutoff - session.expires_at).total_seconds() > hours * 3600:
                to_delete.append(session_id)
        
        for session_id in to_delete:
            self.delete(session_id)
        
        return len(to_delete)
    
    def get_session_statistics(self) -> dict:
        """Get statistics about PQC sessions."""
        sessions = self.get_all()
        return {
            "total": len(sessions),
            "established": len([s for s in sessions if s.status == PQCSessionStatus.ESTABLISHED]),
            "valid": len(self.get_valid_sessions()),
            "expired": len(self.get_expired_sessions()),
            "by_algorithm": {
                algo.value: len([s for s in sessions if s.algorithm == algo])
                for algo in PQCAlgorithmType
            },
            "hybrid_sessions": len([s for s in sessions if s.is_hybrid()]),
        }

