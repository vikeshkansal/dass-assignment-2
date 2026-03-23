"""Tests for property.py."""
import pytest
from moneypoly.player import Player
from moneypoly.property import Property, PropertyGroup


def test_get_rent_mortgaged():
    """Rent on a mortgaged property is 0."""
    prop = Property("Test", 1, 200, 20)
    prop.is_mortgaged = True
    assert prop.get_rent() == 0


def test_get_rent_partial_ownership():
    """Owning 1 of 2 group properties should return base_rent, not doubled."""
    group = PropertyGroup("TestGroup", "blue")
    p = Player("alice")
    prop1 = Property("A", 1, 200, 20, group=group)
    prop2 = Property("B", 3, 200, 20, group=group)
    prop1.owner = p
    # prop2 is unowned
    assert prop1.get_rent() == 20  # base_rent, not 40


def test_get_rent_no_group():
    """Property with no group returns base_rent."""
    prop = Property("Test", 1, 200, 20)
    prop.owner = Player("alice")
    assert prop.get_rent() == 20


def test_mortgage_already_mortgaged():
    """Mortgaging an already-mortgaged property returns 0."""
    prop = Property("Test", 1, 200, 20)
    prop.is_mortgaged = True
    assert prop.mortgage() == 0


def test_mortgage_unmortgaged():
    """Mortgaging sets flag and returns price // 2."""
    prop = Property("Test", 1, 200, 20)
    payout = prop.mortgage()
    assert prop.is_mortgaged is True
    assert payout == 200 // 2


def test_unmortgage_not_mortgaged():
    """Unmortgaging a non-mortgaged property returns 0."""
    prop = Property("Test", 1, 200, 20)
    assert prop.unmortgage() == 0


def test_unmortgage_mortgaged():
    """Unmortgaging clears flag and returns int(mortgage_value * 1.1)."""
    prop = Property("Test", 1, 200, 20)
    prop.is_mortgaged = True
    cost = prop.unmortgage()
    assert prop.is_mortgaged is False
    assert cost == int((200 // 2) * 1.1)


def test_is_available():
    """is_available checks unowned + not mortgaged."""
    prop = Property("Test", 1, 200, 20)
    assert prop.is_available() is True

    prop.owner = Player("alice")
    assert prop.is_available() is False

    prop.owner = None
    prop.is_mortgaged = True
    assert prop.is_available() is False


def test_all_owned_by_none():
    """all_owned_by(None) returns False."""
    group = PropertyGroup("TestGroup", "blue")
    Property("A", 1, 200, 20, group=group)
    assert group.all_owned_by(None) is False


def test_all_owned_by_partial():
    """Owning 1 of 2 should return False."""
    group = PropertyGroup("TestGroup", "blue")
    p = Player("alice")
    prop1 = Property("A", 1, 200, 20, group=group)
    Property("B", 3, 200, 20, group=group)
    prop1.owner = p
    assert group.all_owned_by(p) is False
