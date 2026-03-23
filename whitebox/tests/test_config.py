"""Tests for configuration integrity."""
from moneypoly.config import (
    BOARD_SIZE, JAIL_POSITION, GO_TO_JAIL_POSITION,
    FREE_PARKING_POSITION, INCOME_TAX_POSITION, LUXURY_TAX_POSITION,
)
from moneypoly.board import Board, SPECIAL_TILES
from moneypoly.cards import CHANCE_CARDS, COMMUNITY_CHEST_CARDS


def test_special_tiles_unique():
    """All SPECIAL_TILES positions are unique (no config constant collision)."""
    expected_positions = [
        0, JAIL_POSITION, GO_TO_JAIL_POSITION, FREE_PARKING_POSITION,
        INCOME_TAX_POSITION, LUXURY_TAX_POSITION,
        2, 17, 33,   # community_chest
        7, 22, 36,   # chance
        5, 15, 25, 35,  # railroad
    ]
    assert len(expected_positions) == len(set(expected_positions))

def test_no_property_in_special():
    """No property position overlaps with a SPECIAL_TILES position."""
    board = Board()
    for prop in board.properties:
        assert prop.position not in SPECIAL_TILES

def test_positions_within_bounds():
    """Every position (special + property) is within [0, BOARD_SIZE - 1]."""
    board = Board()

    for pos in SPECIAL_TILES:
        assert 0 <= pos <= BOARD_SIZE - 1

    for prop in board.properties:
        assert 1 <= prop.position <= BOARD_SIZE - 1

    assert JAIL_POSITION < BOARD_SIZE

def test_property_positions_distinct():
    """All property positions are distinct from each other."""
    board = Board()
    positions = [prop.position for prop in board.properties]
    assert len(positions) == len(set(positions))


def test_card_move_to_values():
    """Every 'move_to' card value is within [0, BOARD_SIZE - 1]."""
    for deck_name, deck in [("Chance", CHANCE_CARDS), ("Community Chest", COMMUNITY_CHEST_CARDS)]:
        for card in deck:
            if card["action"] == "move_to":
                assert 0 <= card["value"] <= BOARD_SIZE - 1
