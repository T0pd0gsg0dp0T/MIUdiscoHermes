import random


class SkillSystem:
    def __init__(self) -> None:
        self.attributes: dict[str, int] = {
            "Intellect": 3,
            "Psyche": 3,
            "Physique": 3,
            "Motorics": 3,
        }
        self.skills: dict[str, int] = {
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
        self.skill_groups: dict[str, list[str]] = {
            "Intellect": ["Logic", "Rhetoric", "Encyclopedia", "Conceptualization"],
            "Psyche": ["Volition", "Inland Empire", "Empathy", "Suggestion"],
            "Physique": ["Endurance", "Pain Threshold", "Physical Instrument", "Perception"],
            "Motorics": ["Hand-Eye Coordination", "Reflexes", "Composure", "Savvy"],
        }

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
