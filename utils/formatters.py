"""
Formatting utilities.
"""

from datetime import datetime
from typing import Tuple, Optional


def format_address(address: Tuple[str, int]) -> str:
    """
    Format address tuple to string.
    
    Args:
        address: (host, port) tuple
    
    Returns:
        Formatted address string
    """
    return f"{address[0]}:{address[1]}"


def format_timestamp(dt: Optional[datetime] = None, format: str = "iso") -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object (defaults to now)
        format: Format type (iso, unix, human)
    
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.utcnow()
    
    if format == "iso":
        return dt.isoformat()
    elif format == "unix":
        return str(int(dt.timestamp()))
    elif format == "human":
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        return dt.isoformat()


def format_bytes(size: int, precision: int = 2) -> str:
    """
    Format bytes to human-readable string.
    
    Args:
        size: Size in bytes
        precision: Decimal precision
    
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    unit_index = 0
    size_float = float(size)
    
    while size_float >= 1024.0 and unit_index < len(units) - 1:
        size_float /= 1024.0
        unit_index += 1
    
    return f"{size_float:.{precision}f} {units[unit_index]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.2f}h"
    else:
        days = seconds / 86400
        return f"{days:.2f}d"


def truncate_string(s: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        s: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix

