# MIUdiscoHermes

*A Disco Elysium inspired surreal RPG — Malice in Underland*

## Overview

MIUdiscoHermes is a text-based surreal RPG inspired by *Disco Elysium*, featuring a unique skill system where skills manifest as internal voices, a thought cabinet mechanic, and a world built from the `miu.json` data file.

**Setting:** Malice in Underland — a vast subterranean realm where physics bends to collective unconscious, bioluminescent fungi light streets of compressed bone, and lost things (including you) eventually arrive.

## Features (Planned / In Progress)

- **Skill System** — 16 skills across 4 attributes (Intellect, Psyche, Physique, Motorics)
- **Skill Checks** — 2d6 + skill + attribute vs. difficulty, with narrative outcomes
- **Thought Cabinet** — Internalize concepts for permanent bonuses/penalties and new dialogue
- **Dialogue System** — Branching dialogue with skill-gated options and world flags
- **World Data** — Locations, NPCs, and items defined in `miu.json`
- **Parser** — Robust JSON parser with error handling for world data

## Quick Start

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Validate world data against schema
miu-validate --stats

# Run the game
python main.py
```

## Project Structure

```
MIUdiscoHermes/
├── main.py              # Entry point
├── miu.json             # World data (locations, NPCs, items, skills)
├── pyproject.toml       # Project config
├── engine/
│   ├── __init__.py      # Package init
│   ├── core.py          # GameEngine - main game loop
│   ├── parser.py        # DataParser - loads miu.json
│   └── skills.py        # SkillSystem - skill checks
├── tests/
│   └── test_engine.py   # Unit tests
├── GDD.md               # Game Design Document
└── KanBan/              # Task tracking
```

## Commands

In-game commands:
- `check <skill>` — Test a skill against difficulty 10 (e.g., `check Logic`)
- `exit` — Quit the game

## Development

### Code Style
- **Black** for formatting (`black .`)
- **Ruff** for linting (`ruff check .`)
- **Mypy** for type checking (`mypy engine`)

### Testing
```bash
pytest                    # Run all tests
pytest -v                 # Verbose
pytest --cov=engine       # With coverage
```

## Data Format

The `miu.json` file contains:
- `metadata` — Title, version, description
- `entries` — Keyed by ID, each with `key` (tags) and `content` (description)

Entries with location keywords (Realm, Geographic, Location, City, etc.) become locations; others become entities (NPCs, items, skills).

## License

MIT License — see LICENSE file for details.