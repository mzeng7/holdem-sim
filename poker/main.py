import game
from decimal import *


def main():
    print("Texas hold'em simulator")
    print("Originally developed by Michael Zeng")
    print("-----")
    num_players = int(input("How many players?: "))
    while True:
        try:
            small_blind = Decimal(input("Small blind?: "))
            big_blind = Decimal(input("Big blind?: "))
            break
        except ValueError:
            print('Invalid input detected.')
    g = game.Game(num_players, small_blind, big_blind)
    g.start_game()


if __name__ == '__main__':
    main()