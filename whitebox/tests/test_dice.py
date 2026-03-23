"""Test for dice.py."""
from moneypoly.dice import Dice


def test_doubles_streak_increment():
    """Rolling doubles increments doubles_streak."""
    d = Dice()
    d.die1 = 3
    d.die2 = 3
    d.doubles_streak = 0

    if d.is_doubles():
        d.doubles_streak += 1
    else:
        d.doubles_streak = 0
    assert d.doubles_streak == 1

    d.die1 = 5
    d.die2 = 5
    
    if d.is_doubles():
        d.doubles_streak += 1
    else:
        d.doubles_streak = 0
    assert d.doubles_streak == 2

    d.die1 = 1
    if d.is_doubles():
        d.doubles_streak += 1
    else:
        d.doubles_streak = 0 
    assert d.doubles_streak == 0
