"""
Browser session manager for VPS deployment
Maintains persistent sessions to avoid looking like a bot
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages browser sessions with persistence
    Saves cookies, local storage, and session data
    """
    
    def __init__(self, base_dir: str = "./browser_sessions"):
        """
        Initialize session manager
        
        Args:
            base_dir: Directory to store session data
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def get_session_dir(self, user_id: str) -> Path:
        """Get session directory for a user"""
        session_dir = self.base_dir / user_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir
    
    async def save_session(self, user_id: str, context, metadata: Optional[Dict] = None):
        """
        Save browser session (cookies, storage, etc.)
        
        Args:
            user_id: Unique identifier for this session
            context: Playwright browser context
            metadata: Optional metadata to store with session
        """
        session_dir = self.get_session_dir(user_id)
        
        try:
            # Save storage state (includes cookies)
            storage_path = session_dir / "storage.json"
            storage_state = await context.storage_state()
            
            with open(storage_path, 'w') as f:
                json.dump(storage_state, f, indent=2)
            
            # Save metadata
            if metadata is None:
                metadata = {}
            
            metadata.update({
                "last_saved": datetime.now().isoformat(),
                "user_id": user_id
            })
            
            metadata_path = session_dir / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"💾 Saved session for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save session for {user_id}: {e}")
            return False
    
    async def load_session(self, user_id: str, browser) -> Optional[Any]:
        """
        Load existing browser session if available
        
        Args:
            user_id: Unique identifier for this session
            browser: Playwright browser instance
        
        Returns:
            Browser context with loaded session, or new context if no session exists
        """
        session_dir = self.get_session_dir(user_id)
        storage_path = session_dir / "storage.json"
        metadata_path = session_dir / "metadata.json"
        
        # Check if session exists and is valid
        if not storage_path.exists():
            logger.info(f"📝 No existing session for user: {user_id}")
            return await browser.new_context()
        
        try:
            # Check session age
            metadata = {}
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                last_saved = datetime.fromisoformat(metadata.get("last_saved", "2000-01-01"))
                age_days = (datetime.now() - last_saved).days
                
                # Sessions older than 30 days are considered stale
                if age_days > 30:
                    logger.warning(f"⚠️  Session for {user_id} is {age_days} days old, creating new")
                    return await browser.new_context()
            
            # Load storage state
            with open(storage_path, 'r') as f:
                storage_state = json.load(f)
            
            context = await browser.new_context(storage_state=storage_state)
            logger.info(f"✅ Loaded existing session for user: {user_id}")
            
            return context
            
        except Exception as e:
            logger.error(f"❌ Failed to load session for {user_id}: {e}")
            logger.info("Creating new context instead")
            return await browser.new_context()
    
    def has_session(self, user_id: str) -> bool:
        """
        Check if a valid session exists for user
        
        Args:
            user_id: Unique identifier for this session
        
        Returns:
            True if session exists and is valid
        """
        session_dir = self.get_session_dir(user_id)
        storage_path = session_dir / "storage.json"
        metadata_path = session_dir / "metadata.json"
        
        if not storage_path.exists():
            return False
        
        # Check if session is not too old
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                last_saved = datetime.fromisoformat(metadata.get("last_saved", "2000-01-01"))
                age_days = (datetime.now() - last_saved).days
                
                return age_days <= 30
            except Exception:
                return False
        
        return True
    
    def delete_session(self, user_id: str):
        """
        Delete session for a user
        
        Args:
            user_id: Unique identifier for this session
        """
        session_dir = self.get_session_dir(user_id)
        
        try:
            if session_dir.exists():
                import shutil
                shutil.rmtree(session_dir)
                logger.info(f"🗑️  Deleted session for user: {user_id}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to delete session for {user_id}: {e}")
            return False
    
    def get_session_info(self, user_id: str) -> Optional[Dict]:
        """
        Get information about a session
        
        Args:
            user_id: Unique identifier for this session
        
        Returns:
            Session metadata dict or None
        """
        session_dir = self.get_session_dir(user_id)
        metadata_path = session_dir / "metadata.json"
        storage_path = session_dir / "storage.json"
        
        if not storage_path.exists():
            return None
        
        info = {
            "user_id": user_id,
            "exists": True,
            "storage_file": str(storage_path),
            "storage_size": storage_path.stat().st_size if storage_path.exists() else 0
        }
        
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                info.update(metadata)
                
                # Calculate age
                if "last_saved" in metadata:
                    last_saved = datetime.fromisoformat(metadata["last_saved"])
                    age = datetime.now() - last_saved
                    info["age_hours"] = age.total_seconds() / 3600
                    info["age_days"] = age.days
            except Exception as e:
                logger.error(f"Failed to read metadata: {e}")
        
        return info
    
    def list_sessions(self) -> list[Dict]:
        """
        List all stored sessions
        
        Returns:
            List of session info dicts
        """
        sessions = []
        
        if not self.base_dir.exists():
            return sessions
        
        for user_dir in self.base_dir.iterdir():
            if user_dir.is_dir():
                user_id = user_dir.name
                info = self.get_session_info(user_id)
                if info:
                    sessions.append(info)
        
        return sessions
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """
        Remove sessions older than specified days
        
        Args:
            days_old: Remove sessions older than this many days
        
        Returns:
            Number of sessions removed
        """
        count = 0
        
        for session_info in self.list_sessions():
            user_id = session_info["user_id"]
            age_days = session_info.get("age_days", 0)
            
            if age_days > days_old:
                if self.delete_session(user_id):
                    count += 1
                    logger.info(f"🧹 Removed old session: {user_id} (age: {age_days} days)")
        
        if count > 0:
            logger.info(f"🧹 Cleaned up {count} old sessions")
        
        return count


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager(base_dir: str = "./browser_sessions") -> SessionManager:
    """
    Get global session manager instance (singleton pattern)
    
    Args:
        base_dir: Directory to store session data
    
    Returns:
        SessionManager instance
    """
    global _session_manager
    
    if _session_manager is None:
        _session_manager = SessionManager(base_dir=base_dir)
        logger.info(f"🔧 Session manager initialized (base_dir: {base_dir})")
    
    return _session_manager
