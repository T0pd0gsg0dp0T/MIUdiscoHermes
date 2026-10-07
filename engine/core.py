import os
from typing import Any

from engine.parser import DataParser
from engine.skills import SkillSystem


class GameEngine:
    def __init__(self, data_path: str | None = None) -> None:
        self.running: bool = True
        if data_path is None:
            # Default to miu.json in project root relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_path = os.path.join(base_dir, "miu.json")
        self.parser: DataParser = DataParser(data_path)
        self.skills: SkillSystem = SkillSystem()
        self.current_location_id: str = "1"  # Start at Underland
        self.player_state: dict[str, Any] = {"inventory": [], "flags": {}}
        print("Engine initialized with World Data and Skill System.")

    def run(self) -> None:
        print("Welcome to Malice in Underland.")
        while self.running:
            loc: dict[str, Any] | None = self.parser.get_location(self.current_location_id)
            if not loc:
                print("Error: Current location not found.")
                break

            print(f"\n--- {loc['name']} ---")
            desc: str = loc["description"]
            if len(desc) > 500:
                print(desc[:500] + "...")
            else:
                print(desc)

            # Simple prompt for demonstration
            cmd: str = (
                input("\n(Type 'check [skill]' to test a skill, 'exit' to quit): ").strip().lower()
            )

            if cmd == "exit":
                self.shutdown()
            elif cmd.startswith("check "):
                skill: str = cmd.split(" ", 1)[1]
                success: bool
                val: int
                success, val = self.skills.check(skill, 10)
                result: str = "SUCCESS" if success else "FAILURE"
                print(f"Check {skill}: {val} vs 10 -> {result}")
            else:
                print("Unknown command.")

    def shutdown(self) -> None:
        print("Shutting down...")
        self.running = False
