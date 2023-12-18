import math
from collections import defaultdict
from copy import deepcopy
from read import readInput
from write import writeOutput
from host import GO


class MinMaxPlayer:
    def __init__(self):
        # self.move_order = [[2, 2], [1, 1], [1, 3], [0, 2], [3, 3], [2, 4], [3, 1], [4, 2], [2, 0],
        #                    [0, 0], [0, 1], [2, 3], [0, 3], [0, 4], [1, 4], [2, 1], [3, 4], [4, 4],
        #                    [4, 3], [1, 0], [4, 1], [4, 0], [3, 0], [1, 2], [3, 2]]
        self.move_order = [
            [2, 2],  # 中心
            [1, 1], [3, 3], [1, 3], [3, 1],  # 次级角落
            [1, 2], [3, 2], [2, 1], [2, 3],  # 接近中心
            [2, 0], [2, 4], [0, 2], [4, 2],  # 边缘
            [0, 0], [4, 4], [0, 4], [4, 0],  # 角落
            [0, 1], [0, 3], [1, 0], [1, 4], [3, 0], [3, 4], [4, 1], [4, 3]  # 其他边缘
        ]
    # def calculate_current_score(self, go, opponent_score, eatNum, curPlayer, piece_type):
    #     endangeredScore = 2 * self.pieces_with_one_liberty(go.board, piece_type)
    #     if curPlayer == 0:
    #         return float(opponent_score) + 3 * eatNum - endangeredScore + go.score(piece_type) - go.score(
    #             3 - piece_type)
    #     else:
    #         return float(opponent_score) - 3 * eatNum + endangeredScore - go.score(piece_type) + go.score(
    #             3 - piece_type)
    # def evaluate_board(self, go, player, piece_type):
    #     base_score = go.score(piece_type) - go.score(3 - piece_type)
    #     endangered_pieces = self.pieces_with_one_liberty(go.board, piece_type)
    #     opponent_endangered_pieces = self.pieces_with_one_liberty(go.board, 3 - piece_type)
    #
    #     # 增加评估逻辑：将对方的有威胁的棋子权重加倍
    #     return base_score + 2 * opponent_endangered_pieces - endangered_pieces
    def evaluate_board(self, go, player, piece_type):
        if player == 0:
            base_score = go.score(1) - go.score(2)
            score_modifier = 2.5
        else:
            base_score = go.score(2) - go.score(1)
            score_modifier = -2.5

        return base_score + score_modifier * (1 if piece_type == 1 else -1)

    # def evaluate_board(self, go, player, piece_type):
    #     if player == 0:
    #         base_score = go.score(1) - go.score(2)
    #         score_modifier = 2.5
    #     else:
    #         base_score = go.score(2) - go.score(1)
    #         score_modifier = -2.5
    #
    #     return base_score + score_modifier * (1 if piece_type == 1 else -1)

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

    # def min_max_ab_pruning(self, go, current_player, piece_type, alpha, beta, depth):
    #     if depth > 4:
    #         return [None, self.evaluate_board(go, current_player, piece_type)]
    #
    #     if current_player == 0:
    #         max_val = -math.inf
    #     else:
    #         max_val = math.inf
    #
    #     best_move = None
    #     for move in self.move_order:
    #         if go.valid_place_check(*move, piece_type):
    #             board_copy = deepcopy(go)
    #             board_copy.place_chess(*move, piece_type)
    #             board_copy.remove_died_pieces(3 - piece_type)
    #
    #             _, score = self.min_max_ab_pruning(board_copy, 1 - current_player, 3 - piece_type, alpha, beta,
    #                                                depth + 1)
    #             endangered_score = self.pieces_with_one_liberty(board_copy.board, piece_type)
    #
    #             if current_player == 0:
    #                 final_score = score + 2 * endangered_score
    #                 if final_score > max_val:
    #                     max_val = final_score
    #                     best_move = move
    #                     alpha = max(alpha, max_val)
    #             else:
    #                 final_score = score - 2 * endangered_score
    #                 if final_score < max_val:
    #                     max_val = final_score
    #                     best_move = move
    #                     beta = min(beta, max_val)
    #
    #             if alpha >= beta:
    #                 break
    #
    #     return best_move, max_val

    def min_max_ab_pruning(self, go, current_player, piece_type, alpha, beta, depth):
        if depth > 3:
            return [None, self.evaluate_board(go, current_player, piece_type)]

        best_move = None
        if current_player == 0:
            max_eval = -math.inf
        else:
            max_eval = math.inf

        for move in self.move_order:
            if go.valid_place_check(*move, piece_type):
                board_copy = deepcopy(go)
                board_copy.place_chess(*move, piece_type)
                board_copy.remove_died_pieces(3 - piece_type)

                _, score = self.min_max_ab_pruning(board_copy, 1 - current_player, 3 - piece_type, alpha, beta,
                                                   depth + 1)
                endangered_score = self.pieces_with_one_liberty(board_copy.board, piece_type)

                if current_player == 0:
                    final_score = score + 2 * endangered_score
                    if final_score > max_eval:
                        max_eval = final_score
                        best_move = move
                        alpha = max(alpha, max_eval)
                else:
                    final_score = score - 2 * endangered_score
                    if final_score < max_eval:
                        max_eval = final_score
                        best_move = move
                        beta = min(beta, max_eval)

                if alpha >= beta:
                    break

        return best_move, max_eval


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MinMaxPlayer()
    action, _ = player.min_max_ab_pruning(go, 0, piece_type, -math.inf, math.inf, 0)
    writeOutput(action)
