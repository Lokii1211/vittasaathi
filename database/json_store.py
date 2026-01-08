"""
JSON-based persistent storage
Replaces in-memory dictionaries with file-based storage
"""

import json
from pathlib import Path
from datetime import datetime
from threading import Lock
from typing import Dict, List, Any, Optional
import uuid


class JSONStore:
    """Thread-safe JSON file storage with auto-save"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.lock = Lock()
        self._data: Dict[str, Any] = {}
        self._load()
    
    def _load(self):
        """Load data from file"""
        if self.file_path.exists():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self._data = {}
        else:
            self._data = {}
            self._save()
    
    def _save(self):
        """Save data to file"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False, default=str)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        with self.lock:
            return self._data.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set value for key"""
        with self.lock:
            self._data[key] = value
            self._save()
    
    def delete(self, key: str) -> bool:
        """Delete key"""
        with self.lock:
            if key in self._data:
                del self._data[key]
                self._save()
                return True
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all data"""
        with self.lock:
            return self._data.copy()
    
    def find(self, condition: callable) -> List[Any]:
        """Find all items matching condition"""
        with self.lock:
            return [v for v in self._data.values() if condition(v)]
    
    def update(self, key: str, updates: Dict) -> Optional[Any]:
        """Update specific fields"""
        with self.lock:
            if key in self._data:
                self._data[key].update(updates)
                self._data[key]["updated_at"] = datetime.now().isoformat()
                self._save()
                return self._data[key]
            return None
    
    def generate_id(self) -> str:
        """Generate unique ID"""
        return str(uuid.uuid4())
    
    def count(self) -> int:
        """Count total items"""
        with self.lock:
            return len(self._data)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        with self.lock:
            return key in self._data
