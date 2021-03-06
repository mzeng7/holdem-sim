"""determine_hand.py

This file contains utilities for determining the winning poker hand given lists of cards.
"""

from hands import *
from collections import Counter
from itertools import combinations


class DetermineHand:
    """
    This class contains methods for identifying poker hands given the five cards that comprise them.

    Attributes:
        cards (list): A list of five Card instances comprising a poker hand.
        most_common (dict): Automatically generated hash table of the number of matching cards in the hand.
    """

    def __init__(self, cards):
        if not isinstance(cards, list):
            raise TypeError('The list of cards must be passed in.')
        if len(cards) != 5:
            raise ValueError('The list of cards must have five cards.')
        for c in cards:
            if not isinstance(c, Card):
                raise TypeError('{0} in cards is not a Card'.format(c))
        self.cards = cards
        self.cards.sort(reverse=True)

        # count the number of matching cards, store them in most_common
        num_counts = Counter()
        for card in self.cards:
            num_counts[card.get_num()] += 1
        self.most_common = num_counts.most_common()

    def identify(self):
        """Returns what kind of five-card poker hand is represented in this instance."""
        if not self._no_duplicates():
            raise ValueError("Hand appears to contain multiple of the same card.")
        # store results of flush and straight so that they are not called twice
        flush = self._is_flush()
        straight = self._is_straight()
        if flush and straight:
            if self.cards[0].get_num() == 1 and self.cards[1].get_num() == 5:
                return StraightFlush(5)  # wheel (ace-to-five) straight flush
            return StraightFlush(self.cards[0].get_num())

        elif self._is_quads():
            return FourOfAKind(self.most_common[0][0], self.most_common[1][0])

        elif self._is_full_house():
            return FullHouse(self.most_common[0][0], self.most_common[1][0])

        elif flush:
            return Flush(self.cards)

        elif straight:
            if self.cards[0].get_num() == 1 and self.cards[1].get_num() == 5:
                return Straight(5)  # wheel (ace-to-five) straight
            return Straight(self.cards[0].get_num())

        elif self._is_trips():
            kickers = []
            for c in self.cards:
                if c.get_num() != self.most_common[0][0]:
                    kickers.append(c)
            return ThreeOfAKind(self.most_common[0][0], kickers)

        elif self._is_two_pair():
            paired_cards = []
            kicker = -1
            for e in self.most_common:
                if e[1] == 2:
                    paired_cards.append(e[0])
                if e[1] == 1:
                    kicker = e[0]
            assert kicker > 0
            return TwoPair(paired_cards[0], paired_cards[1], kicker)

        elif self._is_pair():
            paired_cards = [e[0] for e in self.most_common if e[1] == 2]
            paired_card = paired_cards[0]
            kickers = [card for card in self.cards if card.get_num() != paired_card]
            return OnePair(paired_card, kickers)

        else:
            for e in self.most_common:
                if e[1] != 1:
                    # usually handles five-of-a-kind
                    raise ValueError("Hand does not seem to be a valid poker hand.")
            return HighCard(self.cards)

    def _is_straight_flush(self):
        # never called due to optimization
        return self._is_straight() and self._is_flush()

    def _is_quads(self):
        return self.most_common[0][1] == 4

    def _is_full_house(self):
        return len(self.most_common) == 2 and self.most_common[0][1] == 3 and self.most_common[1][1] == 2

    def _is_flush(self):
        suit = self.cards[0].get_suit()
        for c in self.cards:
            if c.get_suit() != suit:
                return False
        return True

    def _is_straight(self):
        offset = 0
        if self.cards[0].get_num() == 1 and (self.cards[1].get_num() == 5 or self.cards[1].get_num() == 13):
            # offset check in the event of the wheel or nut straights, sorted as A5432 and AKQJT, respectively
            offset = 1
        for i in range(4 - offset):
            if self.cards[i + offset].get_num() != self.cards[i + offset + 1].get_num() + 1:
                return False
        return True

    def _is_trips(self):
        return len(self.most_common) == 3 and self.most_common[0][1] == 3

    def _is_two_pair(self):
        return len(self.most_common) == 3 and self.most_common[0][1] == 2

    def _is_pair(self):
        return len(self.most_common) == 4 and self.most_common[0][1] == 2  # second condition here is a sanity check

    def _no_duplicates(self):
        for i in range(len(self.cards)):
            for j in range(i + 1, len(self.cards)):
                if self.cards[i].is_same(self.cards[j]):
                    return False
        return True


def identify_hand(cards):
    """A convenient function for returning the hand representation given five cards."""
    return DetermineHand(cards).identify()


def best_hand(cards):
    """
    Returns the best five-card hand given more than five cards.

    Usually, seven cards will be passed into this function: two for the hole cards, three
    for the flop, one for the turn, and one for the river. The function uses the combinations
    function from Python's itertools module to generate all possible ways to choose
    five cards from the list, then uses get_hand to identify what the hand is, and finally
    uses the built-in max function to determine the best hand of all combinations.

    Parameters:
        cards (list): The list of cards from which the best hand should be identified.

    Returns:
        Hand: A subclass of Hand that corresponds to the best five-card poker hand.
    """
    return max([identify_hand(list(c)) for c in combinations(cards, 5)])
