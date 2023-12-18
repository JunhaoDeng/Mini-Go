import random
import sys
from read import readInput
from write import writeOutput

from host import GO


class RandomPlayer():
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)

    def get_input_from_console(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    possible_placements.append((i, j))

        if not possible_placements:
            return "PASS"
        else:
            print("Possible placements: ", possible_placements)
            while True:
                try:
                    row = int(input("Enter row: "))
                    if row == -1:
                        return "PASS"
                    col = int(input("Enter col: "))
                    if (row, col) in possible_placements:
                        return (row, col)
                    else:
                        print("Invalid input. Try again.")
                except ValueError:
                    print("Invalid input. Try again.")


if __name__ == "__main__":
    N = 5
    # my stone type, the board after my last move, the board after my opponent`s last move
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = RandomPlayer()
    action = player.get_input_from_console(go, piece_type)
    writeOutput(action)
