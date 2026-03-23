"""Tests for board.py."""
from moneypoly.board import Board
from moneypoly.player import Player

def test_get_property_at():
    """get_property_at returns None for non-property, correct Property otherwise."""
    board = Board()
    prop = board.get_property_at(1)
    assert prop is not None
    assert prop.name == "Mediterranean Avenue"
    assert board.get_property_at(2) is None

def test_get_tile_type_special():
    """Special tiles return correct types."""
    board = Board()
    assert board.get_tile_type(0) == "go"
    assert board.get_tile_type(7) == "chance"
    assert board.get_tile_type(10) == "jail"
    assert board.get_tile_type(30) == "go_to_jail"
    assert board.get_tile_type(15) == "railroad"


def test_get_tile_type_property():
    """Position 1 (Mediterranean Avenue) is a property."""
    board = Board()
    assert board.get_tile_type(1) == "property"


def test_get_tile_type_blank():
    """Position 12 (utility, not modelled) returns blank."""
    board = Board()
    assert board.get_tile_type(12) == "blank"


def test_is_purchasable_and_is_special():
    """is_purchasable and is_special for various states."""
    board = Board()
    # Go is not purchasable
    assert board.is_purchasable(0) is False

    # Unowned property is purchasable
    assert board.is_purchasable(1) is True

    # Owned property is not purchasable
    prop = board.get_property_at(1)
    prop.owner = Player("alice")
    assert board.is_purchasable(1) is False

    # Mortgaged unowned property is not purchasable
    prop.owner = None
    prop.is_mortgaged = True
    assert board.is_purchasable(1) is False

    # Go should be special tile, Mediterranean Avenue should not
    assert board.is_special_tile(0) is True
    assert board.is_special_tile(1) is False