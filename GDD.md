# Game Design Document: MIUdiscoHermes

## 1. Narrative Core
**Setting:** Malice in Underland (from miu.json).
**Genre:** Isometric Surreal RPG.
**Core Loop:** Exploration -> Dialogue/Investigation -> Skill Checks -> Internal Monologue -> Thought Cabinet -> World State Change.

## 2. The Skill System
Following the Disco Elysium model, the character does not just "have" skills; the skills are voices in the head.

### Attribute Groups
- Intellect: Logic, Rhetoric, Encyclopedia, Conceptualization.
- Psyche: Volition, Inland Empire, Empathy, Suggestion.
- Physique: Endurance, Pain Threshold, Physical Instrument, Perception.
- Motorics: Hand-Eye Coordination, Reflexes, Composure, Savvy.

### Skill Checks
- Format: Dice Roll (2d6) + Skill Level vs. Difficulty.
- Outcomes: 
    - Success: Unlocks new dialogue, reveals a secret, or changes world state.
    - Failure: Often leads to more interesting narrative paths, "shame" flags, or setbacks.

## 3. The Thought Cabinet
- Thoughts: Abstract concepts encountered in dialogue.
- Internalization: A thought takes time to "research." Once internalized, it provides a permanent bonus or penalty to specific skills or unlocks new dialogue.

## 4. Dialogue & World Interaction
- The Dialogue Tree: A graph of nodes. Nodes can be locked behind skill checks or specific world flags.
- World State: A global dictionary tracking flags (e.g., met_oracle: True).
- miu.json Integration: The world data (locations and NPCs) is loaded from the JSON file. Content is filtered based on the player's current skill levels (e.g., a "Perception" check reveals a hidden detail in the room description).

## 5. Technical Architecture
- Parser: Converts miu.json into a graph of Location and Entity objects.
- State Manager: Handles player stats, inventory, and world flags.
- Game Loop: A text-based (initial) or UI-based (final) loop processing player input and updating the world state.
