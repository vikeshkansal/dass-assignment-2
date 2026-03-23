"""Tests for main.py."""
import pytest
from moneypoly.game import Game


def test_single_player():
    """One player name should raise an error or be rejected."""
    with pytest.raises(Exception):
        Game(["vikesh"])


def test_zero_players():
    """Empty input / 0 players should raise an error."""
    with pytest.raises(Exception):
        Game([])


def test_duplicate_names():
    """Duplicate player names should be rejected."""
    with pytest.raises(Exception):
        Game(["alice", "alice"])
