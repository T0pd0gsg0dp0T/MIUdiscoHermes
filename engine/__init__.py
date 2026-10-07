"""
MIUdiscoHermes Engine Package

Core game engine components for the Malice in Underland RPG.
"""

from engine.core import GameEngine
from engine.parser import DataParser, DataParserError
from engine.skills import SkillSystem

__all__ = [
    "GameEngine",
    "DataParser",
    "DataParserError",
    "SkillSystem",
]

__version__ = "0.1.0"
