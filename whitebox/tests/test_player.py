"""Tests for player.py."""
import pytest
from moneypoly.player import Player
from moneypoly.property import Property
from moneypoly.config import GO_SALARY, STARTING_BALANCE


def test_add_money_negative():
    """add_money(-1) raises ValueError."""
    p = Player("test")
    with pytest.raises(ValueError):
        p.add_money(-1)


def test_add_money_positive():
    """add_money(100) increases balance by 100."""
    p = Player("test")
    old = p.balance
    p.add_money(100)
    assert p.balance == old + 100


def test_deduct_money_negative():
    """deduct_money(-1) raises ValueError."""
    p = Player("test")
    with pytest.raises(ValueError):
        p.deduct_money(-1)


def test_deduct_money_beyond_balance():
    """deduct_money(2000) on balance=1500 goes to -500."""
    p = Player("test", balance=1500)
    p.deduct_money(2000)
    assert p.balance == -500


def test_is_bankrupt():
    """balance=0 is bankrupt; balance=1 is not."""
    p0 = Player("zero", balance=0)
    assert p0.is_bankrupt() is True
    p1 = Player("one", balance=1)
    assert p1.is_bankrupt() is False


def test_move_land_on_go():
    """move from pos 38 by 2 lands on Go (pos 0), GO_SALARY awarded."""
    p = Player("test")
    p.position = 38
    old_balance = p.balance
    new_pos = p.move(2)
    assert new_pos == 0
    assert p.position == 0
    assert p.balance == old_balance + GO_SALARY


def test_move_pass_go():
    """move from pos 38 by 4 passes Go (lands on 2), salary should be awarded."""
    p = Player("test")
    p.position = 38
    old_balance = p.balance
    new_pos = p.move(4)
    assert new_pos == 2
    assert p.balance == old_balance + GO_SALARY


def test_add_property_twice():
    """Adding the same property twice results in only one entry."""
    p = Player("test")
    prop = Property("Test", 1, 100, 10)
    p.add_property(prop)
    p.add_property(prop)
    assert len(p.properties) == 1


def test_remove_property_not_owned():
    """Removing a property the player doesn't own causes no error."""
    p = Player("test")
    prop = Property("Test", 1, 100, 10)
    p.remove_property(prop)
    assert len(p.properties) == 0


def test_net_worth_with_property():
    """net_worth should include property values, not just balance."""
    p = Player("test", balance=1500)
    prop = Property("Test", 1, 100, 10)
    prop.owner = p
    p.add_property(prop)
    assert p.net_worth() == 1500 + 100
