"""
Unit tests for MIUdiscoHermes engine components.
Tests SkillSystem, DataParser, and GameEngine core functionality.
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.core import GameEngine
from engine.parser import DataParser
from engine.skills import SkillSystem


class TestSkillSystem(unittest.TestCase):
    """Tests for the SkillSystem class."""

    def setUp(self):
        self.skills = SkillSystem()

    def test_initial_attributes(self):
        """Verify default attribute values are set correctly."""
        self.assertEqual(self.skills.attributes["Intellect"], 3)
        self.assertEqual(self.skills.attributes["Psyche"], 3)
        self.assertEqual(self.skills.attributes["Physique"], 3)
        self.assertEqual(self.skills.attributes["Motorics"], 3)

    def test_all_16_skills_exist(self):
        """Verify all 16 skills are initialized."""
        expected_skills = [
            "Logic",
            "Rhetoric",
            "Encyclopedia",
            "Conceptualization",
            "Volition",
            "Inland Empire",
            "Empathy",
            "Suggestion",
            "Endurance",
            "Pain Threshold",
            "Physical Instrument",
            "Perception",
            "Hand-Eye Coordination",
            "Reflexes",
            "Composure",
            "Savvy",
        ]
        for skill in expected_skills:
            self.assertIn(skill, self.skills.skills)
            self.assertEqual(self.skills.skills[skill], 2)

    def test_skill_groups_mapping(self):
        """Verify skill-to-attribute group mapping is complete."""
        all_grouped_skills = []
        for group in self.skills.skill_groups.values():
            all_grouped_skills.extend(group)

        # All 16 skills should be in exactly one group
        self.assertEqual(len(all_grouped_skills), 16)
        self.assertEqual(set(all_grouped_skills), set(self.skills.skills.keys()))

    def test_check_unknown_skill_returns_false(self):
        """Unknown skill names should return (False, 0)."""
        success, total = self.skills.check("NonExistentSkill", 10)
        self.assertFalse(success)
        self.assertEqual(total, 0)

    def test_check_returns_tuple(self):
        """Check method should return (bool, int) tuple."""
        result = self.skills.check("Logic", 10)
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], bool)
        self.assertIsInstance(result[1], int)

    def test_check_total_calculation(self):
        """Verify roll + skill + attribute calculation bounds."""
        # Mock random to control the dice roll
        with patch("engine.skills.random.randint", side_effect=[3, 4]):  # roll = 7
            success, total = self.skills.check("Logic", 10)
            # Logic (2) + Intellect (3) + roll (7) = 12
            self.assertEqual(total, 12)
            self.assertTrue(success)

    def test_get_skill_value(self):
        """get_skill_value returns correct base skill level."""
        self.assertEqual(self.skills.get_skill_value("Logic"), 2)
        self.assertEqual(self.skills.get_skill_value("Composure"), 2)
        self.assertEqual(self.skills.get_skill_value("Unknown"), 0)


class TestDataParser(unittest.TestCase):
    """Tests for the DataParser class."""

    def setUp(self):
        # Create a temporary miu.json for testing
        self.test_data = {
            "metadata": {"title": "Test World", "version": "0.1.0"},
            "entries": {
                "1": {
                    "key": ["Test Realm", "Starting Area"],
                    "content": "A test Realm with Geographic features for Location detection.",
                },
                "2": {
                    "key": ["Test NPC", "Character"],
                    "content": "A regular character without location keywords.",
                },
                "3": {
                    "key": ["Test City", "Geographic Location"],
                    "content": "A City that should be detected as a location.",
                },
            },
        }
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()
        self.parser = DataParser(self.temp_file.name)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_loads_json_successfully(self):
        """Parser should load JSON without error."""
        self.assertIsNotNone(self.parser.data)
        self.assertEqual(self.parser.data["metadata"]["title"], "Test World")

    def test_parses_locations_correctly(self):
        """Entries with location keywords should become locations."""
        # Entry 1 has "Realm" and "Location" -> location
        self.assertIn("1", self.parser.locations)
        self.assertEqual(self.parser.locations["1"]["name"], "Test Realm")

        # Entry 3 has "City" and "Geographic" and "Location" -> location
        self.assertIn("3", self.parser.locations)
        self.assertEqual(self.parser.locations["3"]["name"], "Test City")

    def test_parses_entities_correctly(self):
        """Entries without location keywords should become entities."""
        # Entry 2 has no location keywords -> entity
        self.assertIn("2", self.parser.entities)
        self.assertEqual(self.parser.entities["2"]["name"], "Test NPC")

    def test_get_location_returns_correct_data(self):
        """get_location returns location dict with expected fields."""
        loc = self.parser.get_location("1")
        self.assertIsNotNone(loc)
        self.assertEqual(loc["name"], "Test Realm")
        self.assertIn("description", loc)
        self.assertIn("tags", loc)

    def test_get_location_returns_none_for_missing(self):
        """get_location returns None for non-existent ID."""
        self.assertIsNone(self.parser.get_location("999"))

    def test_get_entity_returns_correct_data(self):
        """get_entity returns entity dict with expected fields."""
        ent = self.parser.get_entity("2")
        self.assertIsNotNone(ent)
        self.assertEqual(ent["name"], "Test NPC")

    def test_get_entity_returns_none_for_missing(self):
        """get_entity returns None for non-existent ID."""
        self.assertIsNone(self.parser.get_entity("999"))


class TestDataParserErrorHandling(unittest.TestCase):
    """Tests for DataParser error handling."""

    def test_file_not_found_raises_error(self):
        """Parser should raise DataParserError for missing file."""
        from engine.parser import DataParser, DataParserError

        with self.assertRaises(DataParserError) as cm:
            DataParser("/nonexistent/path/file.json")
        self.assertIn("not found", str(cm.exception).lower())

    def test_corrupted_json_raises_error(self):
        """Parser should raise DataParserError for invalid JSON."""
        from engine.parser import DataParser, DataParserError

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        temp_file.write("{ invalid json }")
        temp_file.close()
        try:
            with self.assertRaises(DataParserError) as cm:
                DataParser(temp_file.name)
            self.assertIn("corrupted", str(cm.exception).lower())
        finally:
            os.unlink(temp_file.name)

    def test_empty_json_raises_error(self):
        """Parser should handle empty JSON file gracefully."""
        from engine.parser import DataParser, DataParserError

        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        temp_file.write("")
        temp_file.close()
        try:
            with self.assertRaises(DataParserError):
                DataParser(temp_file.name)
        finally:
            os.unlink(temp_file.name)

    def test_permission_error_raises_error(self):
        """Parser should raise DataParserError for permission denied."""
        from engine.parser import DataParser, DataParserError

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with self.assertRaises(DataParserError) as cm:
                DataParser("/some/path/file.json")
        self.assertIn("permission denied", str(cm.exception).lower())

    def test_os_error_raises_error(self):
        """Parser should raise DataParserError for OS errors."""
        from engine.parser import DataParser, DataParserError

        with patch("builtins.open", side_effect=OSError("Disk full")):
            with self.assertRaises(DataParserError) as cm:
                DataParser("/some/path/file.json")
        self.assertIn("failed to read", str(cm.exception).lower())


class TestGameEngine(unittest.TestCase):
    """Tests for the GameEngine class."""

    def setUp(self):
        # Create minimal test data
        self.test_data = {
            "metadata": {"title": "Test"},
            "entries": {
                "1": {
                    "key": ["Underland", "Start"],
                    "content": "Starting Realm location for testing.",
                }
            },
        }
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(self.test_data, self.temp_file)
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    @patch("engine.core.DataParser")
    def test_initialization(self, mock_parser_class):
        """Engine initializes with parser, skills, and default state."""
        mock_parser = MagicMock()
        mock_parser.get_location.return_value = {
            "name": "Underland",
            "description": "Test description for the starting area.",
        }
        mock_parser_class.return_value = mock_parser

        engine = GameEngine()

        self.assertTrue(engine.running)
        self.assertEqual(engine.current_location_id, "1")
        self.assertEqual(engine.player_state, {"inventory": [], "flags": {}})
        mock_parser_class.assert_called_once()

    @patch("engine.core.DataParser")
    def test_shutdown_sets_running_false(self, mock_parser_class):
        """shutdown() sets running to False."""
        mock_parser = MagicMock()
        mock_parser.get_location.return_value = {"name": "Test", "description": "Test"}
        mock_parser_class.return_value = mock_parser

        engine = GameEngine()
        engine.shutdown()

        self.assertFalse(engine.running)


class TestMiuJsonStructure(unittest.TestCase):
    """Tests validating the actual miu.json structure."""

    def setUp(self):
        self.miu_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "miu.json"
        )
        with open(self.miu_path) as f:
            self.data = json.load(f)

    def test_metadata_exists(self):
        """miu.json must have metadata section."""
        self.assertIn("metadata", self.data)
        self.assertIn("title", self.data["metadata"])
        self.assertIn("version", self.data["metadata"])

    def test_entries_exist(self):
        """miu.json must have entries section with content."""
        self.assertIn("entries", self.data)
        self.assertGreater(len(self.data["entries"]), 0)

    def test_all_entries_have_key_and_content(self):
        """Every entry must have 'key' array and 'content' string."""
        for uid, entry in self.data["entries"].items():
            self.assertIn("key", entry, f"Entry {uid} missing 'key'")
            self.assertIn("content", entry, f"Entry {uid} missing 'content'")
            self.assertIsInstance(entry["key"], list, f"Entry {uid} key not a list")
            self.assertIsInstance(entry["content"], str, f"Entry {uid} content not a string")
            self.assertGreater(len(entry["key"]), 0, f"Entry {uid} has empty key list")
            self.assertGreater(len(entry["content"]), 0, f"Entry {uid} has empty content")

    def test_expected_skill_entries_exist(self):
        """Core skills from GDD should be present in miu.json."""
        skill_keys = ["Composure", "Inland Empire", "Logic", "Volition"]
        found_skills = set()
        for entry in self.data["entries"].values():
            for key in entry["key"]:
                if key in skill_keys:
                    found_skills.add(key)

        for skill in skill_keys:
            self.assertIn(skill, found_skills, f"Skill '{skill}' not found in miu.json")


class TestGameEngineIntegration(unittest.TestCase):
    """Integration tests for GameEngine with real miu.json data."""

    def setUp(self):
        self.miu_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "miu.json"
        )

    def test_engine_initializes_with_real_data(self):
        """GameEngine should initialize successfully with actual miu.json."""
        engine = GameEngine(self.miu_path)

        self.assertTrue(engine.running)
        self.assertEqual(engine.current_location_id, "1")
        self.assertEqual(engine.player_state, {"inventory": [], "flags": {}})
        self.assertIsNotNone(engine.parser)
        self.assertIsNotNone(engine.skills)

    def test_starting_location_loads_correctly(self):
        """Starting location (Underland) should be loadable from parser."""
        engine = GameEngine(self.miu_path)

        loc = engine.parser.get_location("1")
        self.assertIsNotNone(loc)
        self.assertEqual(loc["name"], "Underland")
        self.assertIn("description", loc)
        self.assertIn("tags", loc)
        self.assertIn("Starting Realm", loc["tags"])

    def test_all_five_locations_parsed(self):
        """All five expected locations from miu.json should be parsed."""
        engine = GameEngine(self.miu_path)

        expected_locations = {
            "1": "Underland",
            "2": "The Bazaar of Whispers",
            "3": "The Archive of Unwritten Histories",
            "4": "The Court of Echoes",
            "5": "The Maw",
        }

        for uid, name in expected_locations.items():
            loc = engine.parser.get_location(uid)
            self.assertIsNotNone(loc, f"Location {uid} not found")
            self.assertEqual(loc["name"], name)

    def test_entities_parsed_separately_from_locations(self):
        """NPCs, items, and skills should be parsed as entities, not locations."""
        engine = GameEngine(self.miu_path)

        # These should be entities
        entity_ids = ["6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
        for uid in entity_ids:
            ent = engine.parser.get_entity(uid)
            self.assertIsNotNone(ent, f"Entity {uid} not found")
            loc = engine.parser.get_location(uid)
            self.assertIsNone(loc, f"Entity {uid} incorrectly classified as location")

    def test_skill_system_integrated(self):
        """SkillSystem should be accessible and functional through engine."""
        engine = GameEngine(self.miu_path)

        # All 16 skills should exist
        expected_skills = [
            "Logic",
            "Rhetoric",
            "Encyclopedia",
            "Conceptualization",
            "Volition",
            "Inland Empire",
            "Empathy",
            "Suggestion",
            "Endurance",
            "Pain Threshold",
            "Physical Instrument",
            "Perception",
            "Hand-Eye Coordination",
            "Reflexes",
            "Composure",
            "Savvy",
        ]
        for skill in expected_skills:
            self.assertIn(skill, engine.skills.skills)
            self.assertEqual(engine.skills.skills[skill], 2)

        # Skill check should work
        success, total = engine.skills.check("Logic", 10)
        self.assertIsInstance(success, bool)
        self.assertIsInstance(total, int)
        self.assertGreaterEqual(total, 2)  # min: roll(2) + skill(2) + attr(3) = 7


if __name__ == "__main__":
    unittest.main(verbosity=2)
