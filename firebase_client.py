"""
Firebase client for Mnemosyne's Shard system.
Implements robust Firebase initialization and error handling.
"""
import os
import sys
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import traceback

import firebase_admin
from firebase_admin import credentials, firestore, exceptions
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter

from config import config

# Initialize module logger
logger = logging.getLogger(__name__)

@dataclass
class ShardMetadata:
    """Metadata for a memory shard."""
    shard_id: str
    created_at: datetime
    updated_at: datetime
    item_count: int
    size_bytes: int
    status: str  # 'active', 'archived', 'corrupted'
    checksum: str
    version: str = "1.0.0"
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Firestore."""
        data = asdict(self)
        # Convert datetime to ISO string for Firestore
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any])