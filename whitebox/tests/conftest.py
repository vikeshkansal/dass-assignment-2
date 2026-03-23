import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from moneypoly.game import Game


@pytest.fixture(autouse=True)
def reset_shared_state():
    """Reset Game class variables and shared board state before/after each test."""
    Game.turn_number = 0
    Game.running = True
    Game.current_index = 0
    for prop in Game.board.properties:
        prop.owner = None
        prop.is_mortgaged = False
    yield
    Game.turn_number = 0
    Game.running = True
    Game.current_index = 0
    for prop in Game.board.properties:
        prop.owner = None
        prop.is_mortgaged = False
