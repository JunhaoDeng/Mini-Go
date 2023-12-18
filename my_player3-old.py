import random
import sys
from read import readInput
from write import writeOutput

from host import GO

# 我的ai需要做的：读棋盘，合理的给出下一步的位置（一个坐标）
class RandomPlayer():
    def __init__(self):
        self.type = 'random'

    def get_next_hand(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        if not possible_placements:
            return "PASS"
        else:
            return random.choice(possible_placements)

if __name__ == "__main__":
    N = 5
    #读到最新的棋盘，
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    #自己拿到手
    go.set_board(piece_type, previous_board, board)
    player = RandomPlayer()
    action = player.get_next_hand(go, piece_type)
    writeOutput(action)