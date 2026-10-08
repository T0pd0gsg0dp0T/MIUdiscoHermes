import random

from engine.parser import DataParser


class SkillSystem:
    # Canonical Disco Elysium 16 skills across 4 attributes
    DEFAULT_ATTRIBUTES: dict[str, int] = {
        "Intellect": 3,
        "Psyche": 3,
        "Physique": 3,
        "Motorics": 3,
    }
    DEFAULT_SKILLS: dict[str, int] = {
        "Logic": 2,
        "Rhetoric": 2,
        "Encyclopedia": 2,
        "Conceptualization": 2,
        "Volition": 2,
        "Inland Empire": 2,
        "Empathy": 2,
        "Suggestion": 2,
        "Endurance": 2,
        "Pain Threshold": 2,
        "Physical Instrument": 2,
        "Perception": 2,
        "Hand-Eye Coordination": 2,
        "Reflexes": 2,
        "Composure": 2,
        "Savvy": 2,
    }
    DEFAULT_SKILL_GROUPS: dict[str, list[str]] = {
        "Intellect": ["Logic", "Rhetoric", "Encyclopedia", "Conceptualization"],
        "Psyche": ["Volition", "Inland Empire", "Empathy", "Suggestion"],
        "Physique": ["Endurance", "Pain Threshold", "Physical Instrument", "Perception"],
        "Motorics": ["Hand-Eye Coordination", "Reflexes", "Composure", "Savvy"],
    }

    def __init__(self, parser: DataParser | None = None) -> None:
        self.attributes: dict[str, int] = self.DEFAULT_ATTRIBUTES.copy()
        self.skills: dict[str, int] = self.DEFAULT_SKILLS.copy()
        self.skill_groups: dict[str, list[str]] = {
            k: v.copy() for k, v in self.DEFAULT_SKILL_GROUPS.items()
        }

        if parser:
            self._load_from_parser(parser)

    def _load_from_parser(self, parser: DataParser) -> None:
        """Load skills and their governing attributes from world data."""
        for attr in ("Intellect", "Psyche", "Physique", "Motorics"):
            skill_entries = parser.get_skills_by_attribute(attr)
            for entry in skill_entries:
                skill_name = entry["name"]
                if skill_name not in self.skills:
                    # New skill from world data — add with default value
                    self.skills[skill_name] = 2
                    self.skill_groups.setdefault(attr, []).append(skill_name)
                # Ensure skill is in correct attribute group
                if skill_name not in self.skill_groups.get(attr, []):
                    # Remove from any other group
                    for other_attr, group in self.skill_groups.items():
                        if skill_name in group and other_attr != attr:
                            group.remove(skill_name)
                            break
                    self.skill_groups.setdefault(attr, []).append(skill_name)

    def check(self, skill_name: str, difficulty: int) -> tuple[bool, int]:
        if skill_name not in self.skills:
            return False, 0

        attr_val: int = 0
        for attr, group in self.skill_groups.items():
            if skill_name in group:
                attr_val = self.attributes[attr]
                break

        roll: int = random.randint(1, 6) + random.randint(1, 6)
        total: int = roll + self.skills[skill_name] + attr_val

        return total >= difficulty, total

    def get_skill_value(self, skill_name: str) -> int:
        return self.skills.get(skill_name, 0)
