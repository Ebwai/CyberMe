import json
import os
from loguru import logger
from config import settings

class StateManager:
    _state = {}

    @classmethod
    def _load_state(cls):
        if not os.path.exists(settings.STATE_FILE_PATH):
            cls._state = {}
            return
        
        try:
            with open(settings.STATE_FILE_PATH, 'r', encoding='utf-8') as f:
                cls._state = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load state file: {e}")
            cls._state = {}

    @classmethod
    def get_last_latest_id(cls, platform: str) -> str:
        """Get the ID of the last processed latest item for a platform."""
        cls._load_state()
        return cls._state.get(platform)

    @classmethod
    def update_latest_id(cls, platform: str, item_id: str):
        """Update the latest processed item ID for a platform."""
        cls._load_state()
        cls._state[platform] = item_id
        
        try:
            # Ensure directory exists (usually F:\DataInput)
            os.makedirs(os.path.dirname(settings.STATE_FILE_PATH), exist_ok=True)
            with open(settings.STATE_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(cls._state, f, indent=4, ensure_ascii=False)
            logger.info(f"Updated {platform} sync-point to: {item_id}")
        except Exception as e:
            logger.error(f"Failed to save state file: {e}")
