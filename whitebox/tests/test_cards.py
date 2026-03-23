"""Tests for cards.py."""
from moneypoly.cards import CardDeck, CHANCE_CARDS, COMMUNITY_CHEST_CARDS


def test_draw_empty():
    """draw() on empty deck returns None."""
    deck = CardDeck([])
    assert deck.draw() is None


def test_draw_wraps():
    """draw() past end wraps back to first card."""
    cards = [{"a": 1}, {"a": 2}]
    deck = CardDeck(cards, shuffle=False)
    deck.draw()  # card 0
    deck.draw()  # card 1
    third = deck.draw()  # wraps to card 0
    assert third == cards[0]


def test_cards_remaining():
    """cards_remaining() decrements after a draw."""
    cards = [{"a": 1}, {"a": 2}, {"a": 3}]
    deck = CardDeck(cards, shuffle=False)
    assert deck.cards_remaining() == 3
    deck.draw()
    assert deck.cards_remaining() == 2


def test_shuffle_on_init():
    """New deck should be shuffled, not in definition order."""
    original_order = [c["description"] for c in CHANCE_CARDS]
    found_different = False
    for _ in range(50):
        deck = CardDeck(CHANCE_CARDS)
        drawn_order = [deck.draw()["description"] for _ in range(len(CHANCE_CARDS))]
        if drawn_order != original_order:
            found_different = True
            break
    assert found_different == True


def test_reshuffle_after_exhaustion():
    """After exhaustion, subsequent draws should come from a reshuffled deck."""
    deck = CardDeck(COMMUNITY_CHEST_CARDS)
    n = len(COMMUNITY_CHEST_CARDS)
    first_pass = [deck.draw()["description"] for _ in range(n)]
    second_pass = [deck.draw()["description"] for _ in range(n)]
    assert first_pass != second_pass