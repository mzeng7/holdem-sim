"""game.py

This file contains core structures relevant to the game of Texas hold'em.
"""

from numpy import random
from hands import *
from determine_hand import best_hand
from copy import copy
from decimal import *


class Deck:
    """Represents an ordinary, 52-card playing deck."""
    def __init__(self):
        """Constructor for the Deck class, just calls reset."""
        self.cards = []
        self.reset()

    def reset(self):
        """Returns the deck to its original 52 card state."""
        self.cards.clear()
        for s in Suit:
            for i in range(1, 14):
                self.cards.append(Card(i, s))

    def shuffle(self):
        """Shuffle the deck."""
        random.shuffle(self.cards)

    def deal(self, player):
        """Deal a player the top card from this deck."""
        player.add_card(self.cards.pop(0))

    def burn_card(self):
        """Discard the top card of the deck."""
        self.cards.pop(0)

    def get_top_card(self):
        """Removes and returns the top card of the deck."""
        return self.cards.pop(0)


class Player:
    def __init__(self, name, seat_num):
        self.name = name
        self.seat = seat_num
        self.cards = []
        self.stack = Decimal(0)
        self.bet = Decimal(0)
        self.sitting_out = False
        self.comments = ""
        self.hand = None

    def add_card(self, card):
        self.cards.append(card)
        assert len(self.cards) <= 2

    def get_hole_cards(self):
        return self.cards

    def print_hole_cards(self):
        print(self.cards)

    def get_seat_num(self):
        return self.seat

    def get_name(self):
        return self.name

    def get_comments(self):
        return self.comments

    def set_comments(self, comment):
        """Comments about player to print in show_game_state, usually bets."""
        self.comments = comment

    def get_stack(self):
        return self.stack

    def change_stack(self, delta):
        self.stack += delta

    def set_stack(self, amount):
        self.stack = amount

    def get_hand(self):
        return self.hand

    def set_hand(self, hand):
        self.hand = hand

    def get_bet(self):
        return self.bet

    def set_bet(self, bet):
        self.bet = bet

    def sit_out(self):
        self.sitting_out = True

    def come_back(self):
        self.sitting_out = False

    def __str__(self):
        return self.name


class Game:
    """
    Represents a game of Texas hold'em.

    In this class, when start_game() is called, all players are dealt their hole cards.
    The gameplay will pause to ask players for their desired actions when it becomes their
    turn to act and they still have chips in their stack.

    Attributes:
        num_players (int): The number of players sitting at this table.
        small_blind (Decimal): The size of the small blind.
        big_blind (Decimal): The size of the big blind.
        show_cards (bool): Whether hole cards should be revealed in the game state printout.
    """
    def __init__(self, num_players, small_blind, big_blind, show_cards=True):
        self.num_players = num_players
        self.show_cards = show_cards
        self.players = [Player(input("Seat {0} name: ".format(i)), i) for i in range(1, num_players + 1)]
        self.board = []
        self.deck = Deck()
        self.deck.shuffle()
        # TODO: self.actions = []
        self.button = self.determine_button(self.players)
        self.players_in_hand = copy(self.players)
        self.pot = Decimal(0)
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.previous_bet = Decimal(0)

    def get_player_at_seat(self, seat_num):
        """Returns Player at the specified seat number."""
        return self.players[seat_num - 1]

    def take_turns(self):
        """Generator which starts from the small blind and rotates clockwise."""
        i = 0
        cached_size = len(self.players_in_hand)
        while i < cached_size:
            if self.players_in_hand[i] is self.button:
                i += 1
                break
            i += 1
        while True:
            try:
                yield self.players_in_hand[i]
                if len(self.players_in_hand) != cached_size:
                    # if player has folded, don't advance index
                    cached_size = len(self.players_in_hand)
                else:
                    i += 1
            except IndexError:
                i = 0

    def show_game_state(self):
        print('-----\nCurrent game state:')
        print('Current pot: ${0}'.format(self.pot))
        if self.board:
            print('Board: {0}'.format(self.board))
        for p in self.players_in_hand:
            if p is self.button:
                button = "[BTN] "
            else:
                button = ""
            if self.show_cards:
                hole_cards = p.get_hole_cards()
            else:
                hole_cards = ""
            print("  Seat {0} [{1}] ({2}) {3}{4} {5}".format(
                p.get_seat_num(), p.get_stack(), p.get_name(), button, hole_cards, p.get_comments()))

    def start_game(self):
        for p in self.players:
            p.set_stack(Decimal(100) * self.big_blind)
        self.play_hand()

    def play_hand(self):
        # PRE-FLOP
        self.deal_hole_cards()
        self.post_blinds()
        self.round_of_betting(blinds=True)

        # FLOP
        if len(self.players_in_hand) == 1:
            self.no_showdown()
            return
        self.show_flop()
        self.round_of_betting()

        # TURN
        if len(self.players_in_hand) == 1:
            self.no_showdown()
            return
        self.show_turn()
        self.round_of_betting()

        # RIVER
        if len(self.players_in_hand) == 1:
            self.no_showdown()
            return
        self.show_river()
        self.round_of_betting()

        # SHOWDOWN
        if len(self.players_in_hand) == 1:
            self.no_showdown()
            return
        self.showdown()

    def determine_button(self, players):
        """Deals every player one card face-up. Highest value card determines button."""
        print("-----\nDealing for position:")
        exposed_cards = []
        for p in players:
            exposed_cards.append(self.deck.get_top_card())
            print("Seat {0} ({1}) dealt {2}".format(p.get_seat_num(), p.get_name(), exposed_cards[-1]))

        max_so_far = exposed_cards[0].get_num()
        players_with_max = []
        for i in range(len(exposed_cards)):
            cur_num = exposed_cards[i].get_num()
            if Card.lt(max_so_far, cur_num):
                max_so_far = cur_num
                players_with_max.clear()
                players_with_max.append(players[i])
            elif cur_num == max_so_far:
                players_with_max.append(players[i])

        if len(players_with_max) > 1:
            print("A tie was detected. Re-dealing the players who tied:")
            return self.determine_button(players_with_max)
        else:
            self.deck.reset()
            self.deck.shuffle()
            print("Button set to seat {0}".format(players_with_max[0].get_seat_num()))
            return players_with_max[0]

    def move_button(self):
        """Moves button one seat to the left."""
        self.button = self.get_player_at_seat((self.button.get_seat_num() + 1) % self.num_players)

    def deal_hole_cards(self):
        print('-----\nNow dealing hole cards:')
        turn_gen = self.take_turns()
        cur_player = next(turn_gen)
        while len(cur_player.get_hole_cards()) < 2:
            self.deck.deal(cur_player)
            if self.show_cards:
                card = str(cur_player.get_hole_cards()[-1])
            else:
                card = ''
            print("Seat {0} ({1}) dealt {2}".format(cur_player.get_seat_num(), cur_player.get_name(), card))
            cur_player = next(turn_gen)
        self.show_game_state()

    def show_next_card(self):
        """Procedure called by show_flop, show_turn, and show_river that exposes one card from deck."""
        card = self.deck.get_top_card()
        self.board.append(card)
        print(card)

    def show_flop(self):
        self.deck.burn_card()
        print('-----\nFLOP:')
        for _ in range(3):
            self.show_next_card()
        self.show_game_state()

    def show_turn(self):
        self.deck.burn_card()
        print('-----\nTURN:', end='')
        self.show_next_card()
        self.show_game_state()

    def show_river(self):
        self.deck.burn_card()
        print('-----\nRIVER:', end='')
        self.show_next_card()
        self.show_game_state()

    def showdown(self):
        # TODO: split pot
        """Sets self.winner to the winner of the previous hand."""
        for p in self.players_in_hand:
            p.set_hand(best_hand(p.get_hole_cards() + self.board))
        max_so_far = self.players_in_hand[0].get_hand()
        winner = self.players_in_hand[0]
        for p in self.players_in_hand:
            if p.get_hand() > max_so_far:
                max_so_far = p.get_hand()
                winner = p
        if self.pot == 0:
            pot_str = ''
        else:
            pot_str = ' ($' + str(self.pot) + ')'
        print('-----\n{0} wins{1} with {2}'.format(winner, pot_str, max_so_far))

    def no_showdown(self):
        assert len(self.players_in_hand) == 1
        winner = self.players_in_hand[0]
        print('-----\n{0} wins ${1}.'.format(winner, self.pot))

    def get_players(self):
        return self.players

    def post_blinds(self):
        turns = self.take_turns()
        small = next(turns)
        big = next(turns)
        if self.num_players == 2:
            small, big = big, small
        self.bet(small, self.small_blind)
        small.set_comments("posts SB: ${0}".format(self.small_blind))
        self.bet(big, self.big_blind)
        big.set_comments("posts BB: ${0}".format(self.big_blind))
        self.show_game_state()

    def round_of_betting(self, blinds=False):
        turns = self.take_turns()
        if blinds:
            next(turns)  # small blind
            next(turns)  # big blind

        first_to_act = next(turns)
        self.get_action(first_to_act)

        for p in turns:
            if (p is first_to_act and self.previous_bet == 0) or \
                    len(self.players_in_hand) == 1 or (0 < self.previous_bet == p.get_bet()):
                break
            self.show_game_state()
            self.get_action(p)

        self.clear_actions()

    def get_action(self, player):
        while True:
            print('Seat {0} ({1}) to act. '.format(player.get_seat_num(), player.get_name()), end='')

            if self.previous_bet != 0.0:
                if player.get_stack() > self.previous_bet:
                    while True:
                        action = input("Fold/Call ${0}/Raise?: ".format(self.previous_bet))
                        action = action.lower()
                        if action == 'fold' or action == 'call' or action == 'raise':
                            break
                        else:
                            print("Invalid input. Valid inputs: fold, call, raise")
                else:
                    while True:
                        action = input("Fold/Call ${0} (all in)?: ".format(player.get_stack()))
                        action = action.lower()
                        if action == 'fold' or action == 'call':
                            break
                        else:
                            print("Invalid input. Valid inputs: fold, call")
            else:
                while True:
                    action = input("Fold/Check/Bet?: ")
                    action = action.lower()
                    if action == 'fold' or action == 'check' or action == 'bet':
                        break
                    else:
                        print("Invalid input. Valid inputs: fold, call, bet")

            if action == "bet" or action == "raise":
                bet_size = Decimal(input("What is {0}'s {1}?: ".format(player.get_name(), action)))
                try:
                    self.bet(player, bet_size)
                    player.set_comments("{0}s: ${1}".format(action, bet_size))
                except ValueError:
                    print("Invalid {0} size.".format(action))
                    continue
            elif action == "call":
                if player.get_stack() < self.previous_bet:
                    self.bet(player, player.get_stack())
                    player.set_comments("calls: ${0}".format(player.get_stack()))
                else:
                    self.bet(player, self.previous_bet)
                    player.set_comments("calls: ${0}".format(self.previous_bet))
            elif action == "check":
                player.set_comments("checks")
            elif action == "fold":
                self.players_in_hand.remove(player)
                player.set_comments("folds")
            else:
                print('Invalid input detected.')
                continue
            break

    def clear_actions(self):
        self.previous_bet = Decimal(0)
        for p in self.players:
            p.set_bet(Decimal(0))
            p.set_comments("")

    def bet(self, player, amount):
        if amount > player.get_stack():
            raise ValueError("Bet amount is greater than stack size of the player.")
        player.change_stack(-amount)
        player.set_bet(amount)
        self.pot += amount
        self.previous_bet = amount

    def is_big_blind(self, player):
        if self.button() + 2 < self.num_players:
            return player.get_seat_num() == self.button() + 2
        return player.get_seat_num() == ((self.button() + 2) % self.num_players) + 1
