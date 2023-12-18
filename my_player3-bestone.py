import math
from copy import deepcopy
from read import readInput
from write import writeOutput
from host import GO

class MinMaxPlayer:
    def __init__(self):
        self.move_order = [[2, 2], [1, 1], [1, 3], [0, 2], [3, 3], [2, 4], [3, 1], [4, 2], [2, 0],
                           [0, 0], [0, 1], [2, 3], [0, 3], [0, 4], [1, 4], [2, 1], [3, 4], [4, 4],
                           [4, 3], [1, 0], [4, 1], [4, 0], [3, 0], [1, 2], [3, 2]]

    def evaluate_board(self, go, cur_player, piece_type):
        if cur_player == 0:
            base_score = go.score(1) - go.score(2)
            if piece_type == 1:
                score = base_score - 2.5
            else:
                score = base_score + 2.5
        else:
            base_score = go.score(2) - go.score(1)
            if piece_type == 1:
                score = base_score + 2.5
            else:
                score = base_score - 2.5
        return score

    def count_liberties(self, board, i, j, piece_type, visited):
        if i < 0 or j < 0 or i > 4 or j > 4 or str(i) + str(j) in visited:
            return 0
        if board[i][j] == 0:
            return 1
        if board[i][j] == 3 - piece_type:
            return 0

        visited.add(str(i) + str(j))
        return sum([
            self.count_liberties(board, i + x, j + y, piece_type, visited)
            for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ])

    def pieces_with_one_liberty(self, board, piece_type):
        visited = set()
        count = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] == piece_type and str(i) + str(j) not in visited:
                    if self.count_liberties(board, i, j, piece_type, set()) == 1:
                        count += 1
        return count

    def min_max_ab_pruning(self, go, cur_player, piece_type, alpha, beta, depth):
        if depth > 3:
            return [None, self.evaluate_board(go, cur_player, piece_type)]

        best_move = None
        if cur_player == 0:
            max_eval = -math.inf
        else:
            max_eval = math.inf

        for move in self.move_order:
            if go.valid_place_check(*move, piece_type):
                new_go = deepcopy(go)
                new_go.place_chess(*move, piece_type)
                eat_num = len(new_go.remove_died_pieces(3 - piece_type))
                _, score = self.min_max_ab_pruning(new_go, 1 - cur_player, 3 - piece_type, alpha, beta, depth + 1)

                endangered_score = 2 * self.pieces_with_one_liberty(new_go.board, piece_type)
                if cur_player == 0:
                    final_score = score + 3 * eat_num - endangered_score + new_go.score(piece_type) - new_go.score(3 - piece_type)
                    if final_score > max_eval:
                        max_eval, best_move = final_score, move
                        alpha = max(alpha, final_score)
                else:
                    final_score = score - 3 * eat_num + endangered_score + new_go.score(3 - piece_type) - new_go.score(piece_type)
                    if final_score < max_eval:
                        max_eval, best_move = final_score, move
                        beta = min(beta, final_score)

                if beta <= alpha:
                    break

        return best_move, max_eval

    def get_input(self, go, piece_type):
        next_move, _ = self.min_max_ab_pruning(go, 0, piece_type, -math.inf, math.inf, 1)
        if next_move is None:
            next_move = "PASS"
        return next_move

if __name__ == "__main__":
    n = 5
    try:
        input = readInput(n)
        piece_type, previous_board, board = input
    except:
        piece_type, previous_board, board = 1, None, None
    go = GO(n)
    go.set_board(piece_type, previous_board, board)
    player = MinMaxPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)
