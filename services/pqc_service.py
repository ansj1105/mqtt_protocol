"""
PQC service for managing Post-Quantum Cryptography sessions.
"""

from typing import Optional, Dict, Any
import time

from models.pqc import PQCSession, PQCAlgorithmType, PQCSessionStatus
from repositories.pqc import PQCSessionRepository
from utils.logger import LoggerMixin
from utils.validators import validate_pqc_algorithm
from utils.crypto import generate_key_pair, simulate_pqc_kem, hash_data, generate_session_id
from config import Config


class PQCService(LoggerMixin):
    """Service for managing PQC sessions."""
    
    def __init__(self, repository: PQCSessionRepository, config: Config):
        self.repository = repository
        self.config = config
    
    async def initiate_handshake(
        self,
        connection_id: str,
        algorithm: str,
        client_public_key: str
    ) -> Dict[str, Any]:
        """
        Initiate PQC handshake.
        
        Args:
            connection_id: Connection ID
            algorithm: PQC algorithm
            client_public_key: Client's public key
        
        Returns:
            Handshake response data
        """
        # Check if PQC is enabled
        if not self.config.pqc.enabled:
            self.logger.warning("PQC handshake attempted but PQC is disabled")
            return {
                "success": False,
                "message": "PQC not enabled on server"
            }
        
        # Validate algorithm
        try:
            validate_pqc_algorithm(algorithm, self.config.pqc.supported_algorithms)
        except Exception as e:
            self.logger.warning(f"Invalid PQC algorithm: {algorithm}")
            return {
                "success": False,
                "message": str(e)
            }
        
        # Create session
        session_id = generate_session_id()
        session = PQCSession(
            id=session_id,
            connection_id=connection_id,
            algorithm=PQCAlgorithmType(algorithm),
            status=PQCSessionStatus.HANDSHAKE_IN_PROGRESS,
            client_public_key=client_public_key
        )
        
        # Generate server keys based on algorithm
        if session.is_hybrid():
            # Hybrid: PQC KEM + classical key exchange
            kem_algo = algorithm.split('_')[0]
            kex_algo = algorithm.split('_')[1] if '_' in algorithm else 'x25519'
            
            # Simulate PQC KEM (in production, use liboqs)
            pqc_pk, pqc_sk, ciphertext = simulate_pqc_kem(kem_algo)
            
            # Generate classical key pair
            kex_private, kex_public = generate_key_pair(kex_algo)
            
            # Combine keys (simplified for MVP)
            server_public_key = f"{kex_public.hex()}:{ciphertext.hex()}"
            
            # Store session (in production, store keys securely)
            shared_secret_data = f"{pqc_sk.hex()}:{kex_private.hex()}".encode()
        else:
            # Pure PQC
            pqc_pk, pqc_sk, ciphertext = simulate_pqc_kem(algorithm)
            server_public_key = ciphertext.hex()
            shared_secret_data = pqc_sk
        
        # Hash the shared secret (never store actual secret)
        session.shared_secret_hash = hash_data(shared_secret_data)
        session.server_public_key = server_public_key
        
        # Establish session
        session.establish(ttl_seconds=3600)  # 1 hour TTL
        
        # Save to repository
        self.repository.create(session_id, session)
        
        self.logger.info(
            f"PQC handshake completed",
            extra={
                "session_id": session_id,
                "connection_id": connection_id,
                "algorithm": algorithm,
                "is_hybrid": session.is_hybrid()
            }
        )
        
        return {
            "success": True,
            "algorithm": algorithm,
            "server_public_key": server_public_key,
            "session_id": session_id
        }
    
    def get_session(self, session_id: str) -> Optional[PQCSession]:
        """Get session by ID."""
        return self.repository.get(session_id)
    
    def get_session_by_connection(self, connection_id: str) -> Optional[PQCSession]:
        """Get active session by connection ID."""
        return self.repository.get_by_connection(connection_id)
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if session is still valid."""
        session = self.repository.get(session_id)
        if not session:
            return False
        return session.is_valid()
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        count = self.repository.cleanup_expired()
        if count > 0:
            self.logger.info(f"Cleaned up {count} expired PQC sessions")
        return count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get PQC session statistics."""
        return self.repository.get_session_statistics()
    
    def get_info(self) -> Dict[str, Any]:
        """Get PQC configuration info."""
        return {
            "enabled": self.config.pqc.enabled,
            "algorithms": {
                "kem": self.config.pqc.algorithms.kem,
                "kex": self.config.pqc.algorithms.kex,
                "hybrid_mode": self.config.pqc.algorithms.hybrid_mode
            },
            "supported_algorithms": self.config.pqc.supported_algorithms,
            "description": "Post-Quantum Cryptography hybrid key exchange support"
        }

