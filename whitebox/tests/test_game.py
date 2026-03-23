"""Tests for game.py."""
import pytest
from unittest.mock import patch
from moneypoly.game import Game
from moneypoly.property import Property
from moneypoly.config import (
    JAIL_FINE, GO_SALARY, INCOME_TAX_AMOUNT, LUXURY_TAX_AMOUNT,
    STARTING_BALANCE, JAIL_POSITION,
)


# advance_turn

def test_advance_turn_empty():
    """advance_turn() on empty players list should not crash."""
    game = Game(["alice", "bob"])
    game.players.clear()
    game.advance_turn()  # Raises ZeroDivisionError


# play_turn

def test_play_turn_in_jail():
    """Jailed player calls _handle_jail_turn and the turn is advanced."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.in_jail = True

    with patch.object(game, '_handle_jail_turn') as mock:
        game.play_turn()

    mock.assert_called_once_with(alice)


def test_play_turn_three_doubles_jail():
    """3 consecutive doubles means player goes to jail."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    game.dice.doubles_streak = 2  # two prior doubles

    with patch('random.randint', return_value=3):  # doubles again
        game.play_turn()

    assert alice.in_jail is True
    assert alice.position == JAIL_POSITION


def test_play_turn_doubles_extra_turn():
    """Doubles with streak < 3 gives extra turn without advancing."""
    game = Game(["alice", "bob"])
    game.current_index = 0

    with patch('random.randint', return_value=3), \
         patch.object(game, '_move_and_resolve'):
        game.play_turn()

    assert game.current_index == 0


def test_play_turn_normal():
    """Normal non-doubles roll moves and advances turn."""
    game = Game(["alice", "bob"])
    game.current_index = 0

    with patch('random.randint', side_effect=[2, 3]), \
         patch.object(game, '_move_and_resolve'):
        game.play_turn()

    assert game.current_index == 1


def test_interactive_menu():
    """play_turn should call interactive_menu before rolling."""
    game = Game(["alice", "bob"])
    alice = game.players[0]

    with patch.object(game, 'interactive_menu') as mock_menu, \
         patch('random.randint', return_value=3), \
         patch.object(game, '_move_and_resolve'):
        game.play_turn()

    mock_menu.assert_called_once_with(alice)


def test_doubles_streak_bleeds():
    """Doubles streak should reset between players' turns."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    bob = game.players[1]

    with patch('random.randint', return_value=3), \
         patch.object(game, '_move_and_resolve'):

        game.play_turn()
        assert game.dice.doubles_streak == 1
        game.play_turn()
        assert game.dice.doubles_streak == 2
        game.play_turn()
        assert alice.in_jail is True

        assert game.current_index == 1
        game.play_turn()

    assert bob.in_jail is False


# _move_and_resolve

def test_move_and_resolve_all_tiles():
    """Each tile type triggers the correct handler."""
    game = Game(["alice", "bob"])
    alice = game.players[0]

    # go_to_jail
    alice.position = 29
    game._move_and_resolve(alice, 1)
    assert alice.in_jail is True
    assert alice.position == JAIL_POSITION

    # Reset
    alice.in_jail = False
    alice.balance = STARTING_BALANCE

    # income_tax
    alice.position = 3
    old_balance = alice.balance
    game._move_and_resolve(alice, 1)
    assert alice.balance == old_balance - INCOME_TAX_AMOUNT

    # luxury_tax
    alice.position = 37
    old_balance = alice.balance
    game._move_and_resolve(alice, 1)
    assert alice.balance == old_balance - LUXURY_TAX_AMOUNT

    # free_parking
    alice.position = 19
    old_balance = alice.balance
    game._move_and_resolve(alice, 1)
    assert alice.balance == old_balance

    # chance
    alice.position = 6
    with patch.object(game, '_apply_card') as mock_ac:
        game._move_and_resolve(alice, 1)
    mock_ac.assert_called_once()

    # community_chest
    alice.position = 1
    with patch.object(game, '_apply_card') as mock_ac:
        game._move_and_resolve(alice, 1)
    mock_ac.assert_called_once()

    # railroad
    alice.position = 4
    old_balance = alice.balance
    game._move_and_resolve(alice, 1)
    assert alice.balance == old_balance

    # property
    alice.position = 0
    with patch.object(game, '_handle_property_tile') as mock_hpt:
        game._move_and_resolve(alice, 1)
    mock_hpt.assert_called_once()


# buy_property

def test_buy_property_exact_balance():
    """balance == price should succeed."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop = game.board.properties[0]
    alice.balance = 60
    result = game.buy_property(alice, prop)
    assert result is True
    assert prop.owner == alice


def test_buy_property_normal():
    """balance < price fails; balance > price succeeds."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop1 = game.board.properties[0]
    alice.balance = 59
    assert game.buy_property(alice, prop1) is False

    prop2 = game.board.properties[1]
    alice.balance = 61
    assert game.buy_property(alice, prop2) is True
    assert prop2.owner == alice


# pay_rent

def test_pay_rent_mortgaged():
    """Mortgaged property has no rent."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    prop = game.board.properties[0]
    prop.owner = bob
    prop.is_mortgaged = True
    old_balance = alice.balance
    game.pay_rent(alice, prop)
    assert alice.balance == old_balance


def test_pay_rent_no_owner():
    """Unowned property has no rent."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop = game.board.properties[0]
    prop.owner = None
    old_balance = alice.balance
    game.pay_rent(alice, prop)
    assert alice.balance == old_balance


def test_pay_rent_normal():
    """Rent should be transferred from tenant to owner."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    prop = game.board.properties[0]  # base_rent=2
    prop.owner = bob
    bob.add_property(prop)
    alice_old = alice.balance
    bob_old = bob.balance
    rent = prop.get_rent()
    game.pay_rent(alice, prop)
    assert alice.balance == alice_old - rent
    assert bob.balance == bob_old + rent


# mortgage_property

def test_mortgage_property():
    """Not owner, already mortgaged, and success cases."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    prop = game.board.properties[0]

    # Not owner
    prop.owner = bob
    assert game.mortgage_property(alice, prop) is False

    # Already mortgaged
    prop.owner = alice
    alice.add_property(prop)
    prop.is_mortgaged = True
    assert game.mortgage_property(alice, prop) is False

    # Success
    prop.is_mortgaged = False
    old_balance = alice.balance
    assert game.mortgage_property(alice, prop) is True
    assert prop.is_mortgaged is True
    assert alice.balance == old_balance + prop.price // 2


# unmortgage_property

def test_unmortgage_property():
    """Not owner, not mortgaged, and success cases."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    prop = game.board.properties[0]

    # Not owner
    prop.owner = bob
    assert game.unmortgage_property(alice, prop) is False

    # Not mortgaged
    prop.owner = alice
    alice.add_property(prop)
    prop.is_mortgaged = False
    assert game.unmortgage_property(alice, prop) is False

    # Success
    prop.is_mortgaged = True
    old_balance = alice.balance
    cost = int((prop.price // 2) * 1.1)
    assert game.unmortgage_property(alice, prop) is True
    assert prop.is_mortgaged is False
    assert alice.balance == old_balance - cost


def test_unmortgage_cant_afford():
    """prop.unmortgage() clears mortgage before balance check."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop = game.board.properties[0]  # price=60, unmortgage cost=33
    prop.owner = alice
    alice.add_property(prop)
    prop.is_mortgaged = True
    alice.balance = 0  # Cannot afford 33

    result = game.unmortgage_property(alice, prop)
    assert result is False
    assert prop.is_mortgaged is True


# trade

def test_trade():
    """if seller doesn't own or if buyer too poor should False."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    prop = game.board.properties[0]

    # Seller doesn't own
    prop.owner = bob
    assert game.trade(alice, bob, prop, 50) is False

    # Buyer too poor
    prop.owner = alice
    alice.add_property(prop)
    bob.balance = 10
    assert game.trade(alice, bob, prop, 50) is False

    # success
    bob.balance = 1000
    assert game.trade(alice, bob, prop, 50) is True
    assert prop.owner == bob
    assert bob.balance == 950
    assert alice.balance == STARTING_BALANCE + 50

# auction_property

def test_auction_all_pass():
    """All players bid 0 means property stays unowned."""
    game = Game(["alice", "bob"])
    prop = game.board.properties[0]

    with patch('moneypoly.ui.safe_int_input', return_value=0):
        game.auction_property(prop)

    assert prop.owner is None


def test_auction_bid_below_min():
    """Bid below minimum increment is rejected."""
    game = Game(["alice", "bob"])
    prop = game.board.properties[0]

    # Alice bids 50; Bob bids 55 (needs 50 + 10 = 60 minimum)
    with patch('moneypoly.ui.safe_int_input', side_effect=[50, 55]):
        game.auction_property(prop)

    assert prop.owner == game.players[0]  # Alice wins


def test_auction_bid_above_balance():
    """Bid above player's balance is rejected."""
    game = Game(["alice", "bob"])
    prop = game.board.properties[0]
    game.players[0].balance = 30

    with patch('moneypoly.ui.safe_int_input', side_effect=[50, 0]):
        game.auction_property(prop)

    assert prop.owner is None


def test_auction_valid_bid():
    """Valid bid means property awarded, winner charged."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop = game.board.properties[0]
    old_balance = alice.balance
    assert old_balance >= 100

    with patch('moneypoly.ui.safe_int_input', side_effect=[100, 0]):
        game.auction_property(prop)

    assert prop.owner == alice
    assert alice.balance == old_balance - 100

# _handle_jail_turn

def test_jail_free_card():
    """Use Get Out of Jail Free card means you get released and card is consumed."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.in_jail = True
    alice.jail_turns = 0
    alice.get_out_of_jail_cards = 1

    with patch('moneypoly.ui.confirm', return_value=True), \
         patch('random.randint', return_value=3), \
         patch.object(game, '_move_and_resolve'):
        game._handle_jail_turn(alice)

    assert alice.in_jail is False
    assert alice.get_out_of_jail_cards == 0


def test_jail_pay_fine():
    """Paying fine should deduct JAIL_FINE from balance."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.in_jail = True
    alice.jail_turns = 0
    alice.get_out_of_jail_cards = 0
    old_balance = alice.balance

    with patch('moneypoly.ui.confirm', return_value=True), \
         patch('random.randint', return_value=3), \
         patch.object(game, '_move_and_resolve'):
        game._handle_jail_turn(alice)

    assert alice.in_jail is False
    assert alice.balance == old_balance - JAIL_FINE


def test_jail_decline_under_3():
    """Decline fine with turns < 3 stays jailed."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.in_jail = True
    alice.jail_turns = 0
    alice.get_out_of_jail_cards = 0

    with patch('moneypoly.ui.confirm', return_value=False):
        game._handle_jail_turn(alice)

    assert alice.in_jail is True
    assert alice.jail_turns == 1


def test_jail_mandatory_release():
    """Decline fine at jail_turns=2 means forced release with fine deducted."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.in_jail = True
    alice.jail_turns = 2
    alice.get_out_of_jail_cards = 0
    old_balance = alice.balance

    with patch('moneypoly.ui.confirm', return_value=False), \
         patch('random.randint', return_value=3), \
         patch.object(game, '_move_and_resolve'):
        game._handle_jail_turn(alice)

    assert alice.in_jail is False
    assert alice.balance == old_balance - JAIL_FINE


def test_jail_fine_bankruptcy():
    """If the mandatory jail fine bankrupts the player that means the player should be eliminated."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.in_jail = True
    alice.jail_turns = 2
    alice.balance = 1  # After JAIL_FINE of 50, balance = -49
    alice.get_out_of_jail_cards = 0

    with patch('moneypoly.ui.confirm', return_value=False), \
         patch.object(game, '_move_and_resolve'):
        game._handle_jail_turn(alice)

    # Player should be eliminated immediately after fine
    assert alice not in game.players


# _card_move_to

def test_card_move_to_backward_salary():
    """Moving backward (new pos < old) awards Go salary."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.position = 30
    old_balance = alice.balance

    game._card_move_to(alice, 10)  # jail position, a special tile

    assert alice.position == 10
    assert alice.balance == old_balance + GO_SALARY


def test_card_move_to_forward_no_salary():
    """Moving forward (new pos >= old) gives no salary."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.position = 5
    old_balance = alice.balance

    game._card_move_to(alice, 20)  # free parking

    assert alice.position == 20
    assert alice.balance == old_balance


def test_card_move_to_railroad():
    """Railroad destination should trigger property handling."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.position = 30

    test_prop = Property("Test Railroad", 5, 200, 25)
    game.board.properties.append(test_prop)
    try:
        with patch.object(game, '_handle_property_tile') as mock:
            game._card_move_to(alice, 5)
        mock.assert_called_once()
    finally:
        game.board.properties.remove(test_prop)


# _card_birthday

def test_card_birthday():
    """Other player with enough funds is deducted; too poor is skipped."""
    game = Game(["alice", "bob", "carol"])
    alice, bob, carol = game.players
    bob.balance = 100
    carol.balance = 5  # too poor for value=10

    bob_old = bob.balance
    carol_old = carol.balance
    alice_old = alice.balance

    game._card_birthday(alice, 10)

    assert bob.balance == bob_old - 10
    assert carol.balance == carol_old
    assert alice.balance == alice_old + 10

# _apply_card

def test_apply_card_none():
    """_apply_card(player, None) returns immediately."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    old_balance = alice.balance
    game._apply_card(alice, None)
    assert alice.balance == old_balance


def test_apply_card_jail():
    """'jail' action sends player to jail."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    card = {"description": "Go to Jail", "action": "jail", "value": 0}
    game._apply_card(alice, card)
    assert alice.in_jail is True


def test_apply_card_collect():
    """'collect' action adds value to player balance."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    old_balance = alice.balance
    card = {"description": "Collect $50", "action": "collect", "value": 50}
    game._apply_card(alice, card)
    assert alice.balance == old_balance + 50


def test_apply_card_unknown():
    """Unknown action string is silently ignored."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    old_balance = alice.balance
    card = {"description": "Mystery", "action": "unknown_action", "value": 0}
    game._apply_card(alice, card)
    assert alice.balance == old_balance


# _check_bankruptcy

def test_check_bankruptcy_not_bankrupt():
    """Non-bankrupt player stays in the game."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    alice.balance = 100
    game._check_bankruptcy(alice)
    assert alice in game.players
    assert alice.is_eliminated is False


def test_check_bankruptcy_bankrupt():
    """Bankrupt player is eliminated, properties released."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop = game.board.properties[0]
    prop.owner = alice
    alice.add_property(prop)
    alice.balance = 0

    game._check_bankruptcy(alice)
    assert alice not in game.players
    assert alice.is_eliminated is True
    assert prop.owner is None


def test_check_bankruptcy_last_in_list():
    """Bankrupting last player in list resets current_index to 0."""
    game = Game(["alice", "bob"])
    game.current_index = 1
    bob = game.players[1]
    bob.balance = 0

    game._check_bankruptcy(bob)
    assert bob not in game.players
    assert game.current_index == 0


def test_trade_bankruptcy():
    """Trade that bankrupts buyer should eliminate the buyer."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    prop = game.board.properties[0]
    prop.owner = alice
    alice.add_property(prop)
    bob.balance = 100

    game.trade(alice, bob, prop, 100)  # Bob's balance = 0

    assert bob.is_bankrupt()
    assert bob not in game.players


def test_auction_bankruptcy():
    """Auction winner reaching balance 0 should be eliminated."""
    game = Game(["alice", "bob"])
    alice = game.players[0]
    prop = game.board.properties[0]
    alice.balance = 100

    with patch('moneypoly.ui.safe_int_input', side_effect=[100, 0]):
        game.auction_property(prop)

    assert alice.is_bankrupt()
    assert alice not in game.players


def test_birthday_bankruptcy():
    """Birthday card that bankrupts other player should eliminate the player."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    bob.balance = 10

    game._card_birthday(alice, 10)  # Bob's balance = 0

    assert bob.is_bankrupt()
    assert bob not in game.players


# find_winner

def test_find_winner_no_players():
    """No players returns None."""
    game = Game(["alice", "bob"])
    game.players.clear()
    assert game.find_winner() is None


def test_find_winner_richest():
    """Should return richest player."""
    game = Game(["alice", "bob"])
    alice, bob = game.players
    alice.balance = 2000
    bob.balance = 1000
    winner = game.find_winner()
    assert winner == alice
