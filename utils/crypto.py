"""
Cryptography utilities for PQC and key exchange.
"""

import os
import hashlib
import secrets
from typing import Tuple, Optional
from cryptography.hazmat.primitives.asymmetric import x25519, x448
from cryptography.hazmat.primitives import serialization
import logging

logger = logging.getLogger(__name__)


def generate_key_pair(algorithm: str = "x25519") -> Tuple[bytes, bytes]:
    """
    Generate a key pair for key exchange.
    
    Args:
        algorithm: Key exchange algorithm (x25519 or x448)
    
    Returns:
        Tuple of (private_key, public_key) as bytes
    """
    try:
        if algorithm == "x25519":
            private_key = x25519.X25519PrivateKey.generate()
        elif algorithm == "x448":
            private_key = x448.X448PrivateKey.generate()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        logger.debug(f"Generated {algorithm} key pair")
        return private_bytes, public_bytes
    
    except Exception as e:
        logger.error(f"Error generating key pair: {e}")
        raise


def create_shared_secret(
    private_key: bytes,
    peer_public_key: bytes,
    algorithm: str = "x25519"
) -> bytes:
    """
    Create shared secret using Diffie-Hellman key exchange.
    
    Args:
        private_key: Our private key
        peer_public_key: Peer's public key
        algorithm: Key exchange algorithm
    
    Returns:
        Shared secret as bytes
    """
    try:
        if algorithm == "x25519":
            private = x25519.X25519PrivateKey.from_private_bytes(private_key)
            public = x25519.X25519PublicKey.from_public_bytes(peer_public_key)
        elif algorithm == "x448":
            private = x448.X448PrivateKey.from_private_bytes(private_key)
            public = x448.X448PublicKey.from_public_bytes(peer_public_key)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        shared_secret = private.exchange(public)
        logger.debug(f"Created shared secret using {algorithm}")
        return shared_secret
    
    except Exception as e:
        logger.error(f"Error creating shared secret: {e}")
        raise


def simulate_pqc_kem(algorithm: str) -> Tuple[bytes, bytes, bytes]:
    """
    Simulate PQC KEM (Key Encapsulation Mechanism).
    In production, use liboqs or similar library.
    
    Args:
        algorithm: PQC algorithm (e.g., kyber512, kyber768, kyber1024)
    
    Returns:
        Tuple of (public_key, secret_key, ciphertext)
    """
    # Simulated key sizes
    key_sizes = {
        "kyber512": (800, 1632, 768),
        "kyber768": (1184, 2400, 1088),
        "kyber1024": (1568, 3168, 1568),
    }
    
    if algorithm not in key_sizes:
        raise ValueError(f"Unsupported PQC algorithm: {algorithm}")
    
    pk_size, sk_size, ct_size = key_sizes[algorithm]
    
    # Generate random bytes (simulation only!)
    public_key = secrets.token_bytes(pk_size)
    secret_key = secrets.token_bytes(sk_size)
    ciphertext = secrets.token_bytes(ct_size)
    
    logger.warning(f"Using SIMULATED {algorithm} KEM - NOT FOR PRODUCTION!")
    return public_key, secret_key, ciphertext


def hash_data(data: bytes, algorithm: str = "sha256") -> str:
    """
    Hash data using specified algorithm.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm
    
    Returns:
        Hex digest of hash
    """
    h = hashlib.new(algorithm)
    h.update(data)
    return h.hexdigest()


def generate_session_id() -> str:
    """
    Generate a secure session ID.
    
    Returns:
        Session ID string
    """
    return secrets.token_urlsafe(32)


def constant_time_compare(a: bytes, b: bytes) -> bool:
    """
    Constant-time comparison to prevent timing attacks.
    
    Args:
        a: First byte string
        b: Second byte string
    
    Returns:
        True if equal, False otherwise
    """
    return secrets.compare_digest(a, b)

