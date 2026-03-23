"""Tests for bank.py."""
import pytest
from moneypoly.bank import Bank
from moneypoly.player import Player


def test_collect_negative():
    """collect(-100) should leave funds unchanged."""
    bank = Bank()
    old_funds = bank.get_balance()
    bank.collect(-100)
    assert bank.get_balance() == old_funds


def test_pay_out_zero():
    """pay_out(0) returns 0, funds unchanged."""
    bank = Bank()
    old_funds = bank.get_balance()
    result = bank.pay_out(0)
    assert result == 0
    assert bank.get_balance() == old_funds


def test_pay_out_insufficient():
    """pay_out(more than funds) raises ValueError."""
    bank = Bank()
    with pytest.raises(ValueError):
        bank.pay_out(bank.get_balance() + 1)


def test_pay_out_valid():
    """pay_out(100) deducts from funds and returns 100."""
    bank = Bank()
    old_funds = bank.get_balance()
    result = bank.pay_out(100)
    assert result == 100
    assert bank.get_balance() == old_funds - 100


def test_give_loan_zero():
    """give_loan with amount=0 does nothing."""
    bank = Bank()
    player = Player("test")
    old_balance = player.balance
    bank.give_loan(player, 0)
    assert player.balance == old_balance
    assert bank.loan_count() == 0


def test_give_loan_valid():
    """give_loan(500) increases player balance and logs the loan, deducts balance from bank."""
    bank = Bank()
    player = Player("test")
    old_balance = player.balance
    old_bank_funds = bank.get_balance()
    bank.give_loan(player, 500)
    assert player.balance == old_balance + 500
    assert bank.loan_count() == 1
    assert bank.get_balance() == old_bank_funds - 500

def test_give_loan_insufficient_funds():
    """give_loan when bank has insufficient funds should be rejected."""
    bank = Bank()
    player = Player("test")
    bank.pay_out(bank.get_balance())
    assert bank.get_balance() == 0
    with pytest.raises((ValueError, Exception)):
        bank.give_loan(player, 500)
