import json
import logging
import time
from pathlib import Path

from src.config import CACHE_DIR, CACHE_TTL

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, cache_dir=None, ttl=None):
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.ttl = ttl if ttl is not None else CACHE_TTL
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_filepath(self, key):
        safe_key = key.replace("/", "_").replace("?", "_").replace("&", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key):
        filepath = self._get_filepath(key)
        if not filepath.exists():
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() - data.get("timestamp", 0) > self.ttl:
                logger.debug(f"Cache expired for key: {key}")
                return None
            logger.debug(f"Cache hit for key: {key}")
            return data.get("content")
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Cache read error for key {key}: {e}")
            return None

    def set(self, key, content):
        filepath = self._get_filepath(key)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"timestamp": time.time(), "content": content}, f, ensure_ascii=False)
            logger.debug(f"Cache set for key: {key}")
        except (OSError, TypeError) as e:
            logger.warning(f"Cache write error for key {key}: {e}")

    def clear(self):
        for filepath in self.cache_dir.glob("*.json"):
            try:
                filepath.unlink()
            except OSError:
                pass
        logger.info("Cache cleared")

    def remove(self, key):
        filepath = self._get_filepath(key)
        if filepath.exists():
            filepath.unlink()
