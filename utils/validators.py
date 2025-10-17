"""
Validation utilities.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_message_size(message: str, max_size: int) -> bool:
    """
    Validate message size.
    
    Args:
        message: Message to validate
        max_size: Maximum allowed size in bytes
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If message exceeds max size
    """
    size = len(message.encode('utf-8'))
    if size > max_size:
        logger.warning(f"Message size {size} exceeds limit {max_size}")
        raise ValidationError(f"Message size {size} exceeds limit {max_size} bytes")
    return True


def validate_connection_limit(current: int, max_connections: int) -> bool:
    """
    Validate connection limit.
    
    Args:
        current: Current number of connections
        max_connections: Maximum allowed connections
    
    Returns:
        True if under limit
    
    Raises:
        ValidationError: If limit exceeded
    """
    if current >= max_connections:
        logger.warning(f"Connection limit reached: {current}/{max_connections}")
        raise ValidationError(f"Maximum connections ({max_connections}) reached")
    return True


def validate_client_id(client_id: str) -> bool:
    """
    Validate client ID format.
    
    Args:
        client_id: Client ID to validate
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If invalid format
    """
    if not client_id or len(client_id) == 0:
        raise ValidationError("Client ID cannot be empty")
    
    if len(client_id) > 255:
        raise ValidationError("Client ID too long")
    
    return True


def validate_pqc_algorithm(algorithm: str, supported: list) -> bool:
    """
    Validate PQC algorithm.
    
    Args:
        algorithm: Algorithm to validate
        supported: List of supported algorithms
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If algorithm not supported
    """
    if algorithm not in supported:
        logger.warning(f"Unsupported PQC algorithm: {algorithm}")
        raise ValidationError(
            f"Algorithm '{algorithm}' not supported. "
            f"Supported algorithms: {', '.join(supported)}"
        )
    return True


def validate_tc375_protocol(protocol: str, supported: list) -> bool:
    """
    Validate TC375 protocol version.
    
    Args:
        protocol: Protocol version to validate
        supported: List of supported protocols
    
    Returns:
        True if valid
    
    Raises:
        ValidationError: If protocol not supported
    """
    if protocol not in supported:
        logger.warning(f"Unsupported TC375 protocol: {protocol}")
        raise ValidationError(
            f"Protocol '{protocol}' not supported. "
            f"Supported protocols: {', '.join(supported)}"
        )
    return True


def sanitize_input(data: str, max_length: int = 1000) -> str:
    """
    Sanitize user input.
    
    Args:
        data: Input data to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    # Remove null bytes
    data = data.replace('\x00', '')
    
    # Trim to max length
    if len(data) > max_length:
        data = data[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return data.strip()

