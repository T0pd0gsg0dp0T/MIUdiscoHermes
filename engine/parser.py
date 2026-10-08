import json
import logging
from pathlib import Path
from typing import Any

import jsonschema

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataParserError(Exception):
    """Custom exception for DataParser errors."""

    pass


class DataParser:
    """Parses miu.json into typed location/entity indexes with schema validation."""

    # Keywords that classify an entry as a location
    LOCATION_KEYWORDS: tuple[str, ...] = (
        "Realm",
        "Geographic",
        "Location",
        "City",
        "Parish",
        "District",
        "Library",
        "Abyss",
    )

    def __init__(self, json_path: str) -> None:
        self.json_path: str = json_path
        self.data: dict[str, Any] = self._load_json()
        self._validate_schema()

        # Primary lookup tables
        self.locations: dict[str, dict[str, Any]] = {}
        self.entities: dict[str, dict[str, Any]] = {}

        # Secondary indexes for fast queries
        self._by_type: dict[str, list[str]] = {}  # type -> [uids]
        self._by_tag: dict[str, list[str]] = {}  # tag -> [uids]
        self._by_attribute: dict[str, list[str]] = {}  # attribute -> [skill uids]

        self._parse_entries()
        self._build_indexes()

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

    def _validate_schema(self) -> None:
        """Validate loaded data against JSON Schema."""
        schema_path = Path(__file__).parent.parent / "schemas" / "miu_schema.json"
        try:
            with open(schema_path, encoding="utf-8") as f:
                schema = json.load(f)
        except FileNotFoundError:
            logger.warning(f"Schema file not found at {schema_path}, skipping validation")
            return
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid schema JSON: {e}, skipping validation")
            return

        try:
            jsonschema.validate(instance=self.data, schema=schema)
            logger.info("Schema validation passed")
        except jsonschema.ValidationError as e:
            logger.error(f"Schema validation failed: {e.message}")
            raise DataParserError(f"World data schema invalid: {e.message}") from e

    def _parse_entries(self) -> None:
        """Classify entries into locations and entities."""
        entries = self.data.get("entries", {})
        for uid, entry in entries.items():
            content: str = entry.get("content", "")
            keys: list[str] = entry.get("key", [])
            searchable_text = content + " " + " ".join(keys)

            is_location = any(word in searchable_text for word in self.LOCATION_KEYWORDS)

            parsed = {
                "name": keys[0] if keys else f"Entry {uid}",
                "description": content,
                "tags": keys,
            }

            if is_location:
                self.locations[uid] = parsed
                self._index_by_type(uid, "location")
            else:
                self.entities[uid] = parsed
                # Determine entity subtype from tags
                subtype = self._infer_entity_subtype(keys)
                self._index_by_type(uid, subtype)

            # Index all tags
            for tag in keys:
                self._index_by_tag(tag, uid)

    def _infer_entity_subtype(self, keys: list[str]) -> str:
        """Infer entity subtype from tags."""
        key_lower = [k.lower() for k in keys]
        if "skill" in key_lower:
            return "skill"
        if "npc" in key_lower:
            return "npc"
        if "item" in key_lower:
            return "item"
        return "entity"

    def _build_indexes(self) -> None:
        """Build attribute->skills index for skill system integration."""
        for uid, entry in self.data.get("entries", {}).items():
            keys = entry.get("key", [])
            key_lower = [k.lower() for k in keys]
            if "skill" in key_lower:
                # Find which attribute this skill belongs to
                for attr in ("Intellect", "Psyche", "Physique", "Motorics"):
                    if attr in keys:
                        self._index_by_attribute(attr, uid)
                        break

    def _index_by_type(self, uid: str, type_: str) -> None:
        self._by_type.setdefault(type_, []).append(uid)

    def _index_by_tag(self, tag: str, uid: str) -> None:
        self._by_tag.setdefault(tag, []).append(uid)

    def _index_by_attribute(self, attr: str, uid: str) -> None:
        self._by_attribute.setdefault(attr, []).append(uid)

    # --- Public query methods ---

    def get_location(self, uid: str) -> dict[str, Any] | None:
        return self.locations.get(uid)

    def get_entity(self, uid: str) -> dict[str, Any] | None:
        return self.entities.get(uid)

    def get_by_type(self, type_: str) -> list[dict[str, Any]]:
        """Return all entries of a given type (location, npc, item, skill)."""
        uids = self._by_type.get(type_, [])
        results = []
        for uid in uids:
            if uid in self.locations:
                results.append(self.locations[uid])
            elif uid in self.entities:
                results.append(self.entities[uid])
        return results

    def get_by_tag(self, tag: str) -> list[dict[str, Any]]:
        """Return all entries tagged with the given tag."""
        uids = self._by_tag.get(tag, [])
        results = []
        for uid in uids:
            if uid in self.locations:
                results.append(self.locations[uid])
            elif uid in self.entities:
                results.append(self.entities[uid])
        return results

    def get_skills_by_attribute(self, attribute: str) -> list[dict[str, Any]]:
        """Return all skills governed by the given attribute."""
        uids = self._by_attribute.get(attribute, [])
        return [self.entities[uid] for uid in uids if uid in self.entities]

    def all_location_ids(self) -> list[str]:
        return list(self.locations.keys())

    def all_entity_ids(self) -> list[str]:
        return list(self.entities.keys())

    def get_types(self) -> list[str]:
        return list(self._by_type.keys())

    def get_tags(self) -> list[str]:
        return list(self._by_tag.keys())
