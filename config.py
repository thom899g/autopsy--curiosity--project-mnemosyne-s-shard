"""
Configuration management for Mnemosyne's Shard system.
Implements robust configuration loading with validation and defaults.
"""
import os
import sys
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

from pydantic import BaseSettings, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LogLevel(str, Enum):
    """Valid log levels for the system."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class SystemConfig(BaseSettings):
    """Main system configuration with validation."""
    
    # Firebase Configuration
    google_application_credentials: str = Field(
        default="./service-account-key.json",
        description="Path to Firebase service account key"
    )
    firebase_project_id: str = Field(
        default="mnemosyne-dev",
        description="Firebase project ID"
    )
    
    # API Configuration
    deepseek_api_key: Optional[str] = Field(
        default=None,
        description="DeepSeek API key (optional)"
    )
    api_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        description="Base URL for API calls"
    )
    
    # System Configuration
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )
    shard_batch_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Number of items per shard batch"
    )
    max_retry_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum retry attempts for operations"
    )
    shard_retention_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Days to retain shards before archival"
    )
    
    # Validation
    @validator('google_application_credentials')
    def validate_credentials_path(cls, v: str) -> str:
        """Validate that credentials file exists."""
        if not os.path.exists(v):
            logging.warning(f"Credentials file not found at {v}")
        return v
    
    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"

def get_config() -> SystemConfig:
    """
    Get system configuration with proper initialization.
    
    Returns:
        SystemConfig: Validated configuration object
        
    Raises:
        ValueError: If critical configuration is missing
    """
    try:
        config = SystemConfig()
        
        # Validate critical configuration
        if not os.path.exists(config.google_application_credentials):
            # Try to find in common locations
            alt_paths = [
                "service-account-key.json",
                "../service-account-key.json",
                os.path.expanduser("~/service-account-key.json")
            ]
            
            for path in alt_paths:
                if os.path.exists(path):
                    config.google_application_credentials = path
                    break
        
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        raise ValueError(f"Configuration error: {e}")

# Global configuration instance
config = get_config()