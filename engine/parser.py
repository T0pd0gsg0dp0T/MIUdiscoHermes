import json
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataParserError(Exception):
    """Custom exception for DataParser errors."""

    pass


class DataParser:
    def __init__(self, json_path: str) -> None:
        self.json_path: str = json_path
        self.data: dict[str, Any] = self._load_json()
        self.locations: dict[str, dict[str, Any]] = {}
        self.entities: dict[str, dict[str, Any]] = {}
        self._parse_entries()

    def _load_json(self) -> dict[str, Any]:
        """Load and parse JSON file with comprehensive error handling."""
        try:
            with open(self.json_path, encoding="utf-8") as f:
                return json.load(f)  # type: ignore[no-any-return]
        except FileNotFoundError as e:
            logger.error(f"JSON file not found: {self.json_path}")
            raise DataParserError(f"World data file not found: {self.json_path}") from e
        except json.JSONDecodeError as e:
            logger.error(
                f"Corrupted JSON in {self.json_path}: {e.msg} at line {e.lineno}, column {e.colno}"
            )
            raise DataParserError(f"Corrupted world data (line {e.lineno}): {e.msg}") from e
        except PermissionError as e:
            logger.error(f"Permission denied reading {self.json_path}")
            raise DataParserError(
                f"Cannot read world data file (permission denied): {self.json_path}"
            ) from e
        except OSError as e:
            logger.error(f"OS error reading {self.json_path}: {e}")
            raise DataParserError(f"Failed to read world data: {e}") from e

    def _parse_entries(self) -> None:
        entries = self.data.get("entries", {})
        location_keywords: list[str] = [
            "Realm",
            "Geographic",
            "Location",
            "City",
            "Parish",
            "District",
            "Library",
            "Abyss",
        ]
        for uid, entry in entries.items():
            content: str = entry.get("content", "")
            keys: list[str] = entry.get("key", [])
            # Check both content and tags for location keywords
            searchable_text = content + " " + " ".join(keys)
            if any(word in searchable_text for word in location_keywords):
                self.locations[uid] = {
                    "name": keys[0] if keys else f"Location {uid}",
                    "description": content,
                    "tags": keys,
                }
            else:
                self.entities[uid] = {
                    "name": keys[0] if keys else f"Entity {uid}",
                    "description": content,
                    "tags": keys,
                }

    def get_location(self, uid: str) -> dict[str, Any] | None:
        return self.locations.get(uid)

    def get_entity(self, uid: str) -> dict[str, Any] | None:
        return self.entities.get(uid)
