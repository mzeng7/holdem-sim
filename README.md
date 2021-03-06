# holdem-sim

HoldemSim is a simulator for Texas hold'em.

Texas hold'em is a variant of poker where each player starts with two cards face-down (the "hole cards").
After a round of betting, three cards are exposed face-up (called "the flop"). After another round of
betting, an additional card is exposed face-up (called "the turn"), and after a round of betting, a fifth
and final card (called "the river") is exposed face-up. A player's hand is the best five-card poker hand
among the seven cards exposed to them: their hole cards, the flop, the turn, and the river.

## Running the text-based simulation

Clone this repository, then run in the console:

    cd poker
    python3 main.py

## Django web framework

Currently, within the Django web framework, code is written which allow users to create accounts and maintain user profiles. This will be expanded in the near future to allow access to the poker simulation.

## Descriptions

* **main.py:** Asks for number and names of players, then simulates rounds of Texas hold'em in the console.
* **determine_hand.py:** This file contains utilities for determining the winning poker hand given lists of cards.
	* Contains the logic for determining what kind of poker hand we have given the cards.
* **game.py:** This file contains core structures relevant to the game of Texas hold'em.
	* Contains classes that represent a deck of cards, a game of poker, etc.
* **hands.py:** This file contains a number of structures representing objects relevant to playing cards and poker hands.
	* Contains classes that represent a playing card, a suit, and the kinds of poker hands like straights, flushes, and full houses.

## Known issues

* Six is not pluralized correctly in hands.py (e.g. ""Two pair, fives full of sixs"")
* Currently, only one hand at a time is supported.
* No logic exists to allow players to move ALL IN properly.
	* In the same vein, no logic exists to calculate side pots.
* If a player has already placed a bet and was raised, they only need to call the difference.
