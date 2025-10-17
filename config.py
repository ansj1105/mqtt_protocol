"""
Configuration management module for WebSocket server.
Handles both environment variables and config.json settings.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ServerConfig(BaseModel):
    """Server configuration."""
    host: str = Field(default="0.0.0.0")
    websocket_port: int = Field(default=8765)
    api_port: int = Field(default=8080)


class TLSConfig(BaseModel):
    """TLS/SSL configuration."""
    enabled: bool = Field(default=True)
    cert_path: str = Field(default="./certs/server.crt")
    key_path: str = Field(default="./certs/server.key")
    ca_path: Optional[str] = Field(default="./certs/ca.crt")


class PQCAlgorithms(BaseModel):
    """PQC algorithm configuration."""
    kem: str = Field(default="kyber768")
    kex: str = Field(default="x25519")
    hybrid_mode: bool = Field(default=True)


class PQCConfig(BaseModel):
    """Post-Quantum Cryptography configuration."""
    enabled: bool = Field(default=True)
    algorithms: PQCAlgorithms = Field(default_factory=PQCAlgorithms)
    supported_algorithms: List[str] = Field(
        default_factory=lambda: [
            "kyber512",
            "kyber768",
            "kyber1024",
            "kyber768_x25519",
            "kyber1024_x448"
        ]
    )


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = Field(default=True)
    max_requests_per_minute: int = Field(default=60)


class SecurityConfig(BaseModel):
    """Security configuration."""
    max_message_size: int = Field(default=1048576)  # 1MB
    connection_timeout: int = Field(default=300)  # 5 minutes
    max_connections: int = Field(default=1000)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)


class TC375Config(BaseModel):
    """TC375 Litekit configuration."""
    client_timeout: int = Field(default=30)
    max_retries: int = Field(default=3)
    supported_protocols: List[str] = Field(default_factory=lambda: ["v1", "v2"])
    default_protocol: str = Field(default="v2")


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    file: str = Field(default="./logs/server.log")
    console: bool = Field(default=True)


class Config(BaseModel):
    """Main configuration class."""
    server: ServerConfig = Field(default_factory=ServerConfig)
    tls: TLSConfig = Field(default_factory=TLSConfig)
    pqc: PQCConfig = Field(default_factory=PQCConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    tc375: TC375Config = Field(default_factory=TC375Config)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def from_json(cls, config_path: str = "config.json") -> "Config":
        """Load configuration from JSON file."""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return cls(**data)
        return cls()

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        config = cls()
        
        # Server settings
        if os.getenv("SERVER_HOST"):
            config.server.host = os.getenv("SERVER_HOST")
        if os.getenv("SERVER_WS_PORT"):
            config.server.websocket_port = int(os.getenv("SERVER_WS_PORT"))
        if os.getenv("SERVER_API_PORT"):
            config.server.api_port = int(os.getenv("SERVER_API_PORT"))
        
        # TLS settings
        if os.getenv("TLS_ENABLED"):
            config.tls.enabled = os.getenv("TLS_ENABLED").lower() == "true"
        if os.getenv("TLS_CERT_PATH"):
            config.tls.cert_path = os.getenv("TLS_CERT_PATH")
        if os.getenv("TLS_KEY_PATH"):
            config.tls.key_path = os.getenv("TLS_KEY_PATH")
        
        # PQC settings
        if os.getenv("PQC_ENABLED"):
            config.pqc.enabled = os.getenv("PQC_ENABLED").lower() == "true"
        if os.getenv("PQC_ALGORITHM"):
            algorithm = os.getenv("PQC_ALGORITHM")
            if "_" in algorithm:
                kem, kex = algorithm.split("_", 1)
                config.pqc.algorithms.kem = kem
                config.pqc.algorithms.kex = kex
        
        # Logging settings
        if os.getenv("LOG_LEVEL"):
            config.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FORMAT"):
            config.logging.format = os.getenv("LOG_FORMAT")
        
        # Security settings
        if os.getenv("MAX_MESSAGE_SIZE"):
            config.security.max_message_size = int(os.getenv("MAX_MESSAGE_SIZE"))
        if os.getenv("CONNECTION_TIMEOUT"):
            config.security.connection_timeout = int(os.getenv("CONNECTION_TIMEOUT"))
        if os.getenv("MAX_CONNECTIONS"):
            config.security.max_connections = int(os.getenv("MAX_CONNECTIONS"))
        
        # TC375 settings
        if os.getenv("TC375_CLIENT_TIMEOUT"):
            config.tc375.client_timeout = int(os.getenv("TC375_CLIENT_TIMEOUT"))
        if os.getenv("TC375_MAX_RETRIES"):
            config.tc375.max_retries = int(os.getenv("TC375_MAX_RETRIES"))
        
        return config

    @classmethod
    def load(cls, config_path: str = "config.json") -> "Config":
        """
        Load configuration with priority: env vars > config.json > defaults
        """
        # Start with JSON config
        config = cls.from_json(config_path)
        
        # Override with environment variables
        env_config = cls.from_env()
        
        # Merge configurations (env vars take precedence)
        if os.getenv("SERVER_HOST"):
            config.server = env_config.server
        if os.getenv("TLS_ENABLED") or os.getenv("TLS_CERT_PATH"):
            config.tls = env_config.tls
        if os.getenv("PQC_ENABLED") or os.getenv("PQC_ALGORITHM"):
            config.pqc = env_config.pqc
        if os.getenv("LOG_LEVEL"):
            config.logging = env_config.logging
        
        return config


# Global configuration instance
_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None or reload:
        _config = Config.load()
    return _config


def init_config(config_path: str = "config.json") -> Config:
    """Initialize the configuration."""
    global _config
    _config = Config.load(config_path)
    return _config

