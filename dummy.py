import math
import time
from copy import deepcopy
from read import readInput
from write import writeOutput
from host import GO


class MinMaxPlayer:
    def __init__(self):
        self.move_order = [[2, 2], [1, 1], [1, 3], [0, 2], [3, 3], [2, 4], [3, 1], [4, 2], [2, 0],
                           [0, 0], [0, 1], [2, 3], [0, 3], [0, 4], [1, 4], [2, 1], [3, 4], [4, 4],
                           [4, 3], [1, 0], [4, 1], [4, 0], [3, 0], [1, 2], [3, 2]]
        self.transposition_table = {}
        self.zobrist_table = self.init_zobrist()
    def opponent(self, piece_type):
        return 3 - piece_type
    def init_zobrist(self):
        import random
        table = {}
        for i in range(5):
            for j in range(5):
                for k in [1, 2]:
                    table[(i, j, k)] = random.getrandbits(64)
        return table
    def compute_hash(self, board):
        h = 0
        for i in range(5):
            for j in range(5):
                if board[i][j] != 0:
                    h ^= self.zobrist_table[(i, j, board[i][j])]
        return h
    def heuristic_move_order(self, go, piece_type):
        moves_heuristic = {}

        for move in self.move_order:
            if go.valid_place_check(*move, piece_type):
                heuristic_val = self.calculate_heuristic(go, move, piece_type)
                moves_heuristic[tuple(move)] = heuristic_val

        sorted_moves = sorted(moves_heuristic, key=moves_heuristic.get, reverse=True)

        return sorted_moves
    def calculate_heuristic(self, go, move, piece_type):
        new_go = deepcopy(go)
        new_go.place_chess(*move, piece_type)
        new_go.remove_died_pieces(self.opponent(piece_type))
        heuristic_val = self.evaluate_board(new_go, 0, piece_type)
        heuristic_val += self.check_aggressive_shapes(new_go.board, *move)
        heuristic_val -= self.check_defensive_shapes(new_go.board, *move)
        if piece_type == 1:
            factor = 1
        else:
        opp_liberties_before = self.total_chain_liberties(go.board, self.opponent(piece_type))
        opp_liberties_after = self.total_chain_liberties(new_go.board, self.opponent(piece_type))
        heuristic_val += (opp_liberties_before - opp_liberties_after) * factor
        my_liberties_before = self.total_chain_liberties(go.board, piece_type)
        my_liberties_after = self.total_chain_liberties(new_go.board, piece_type)
        heuristic_val += (my_liberties_after - my_liberties_before) * factor
        return heuristic_val

    def distance_to_center(self, i, j):
        center = 2
        return abs(i - center) + abs(j - center)

    def check_aggressive_shapes(self, board, i, j):
        if 0 <= i + 2 < 5:
            if board[i + 1][j] == 1 and board[i + 2][j] == 1:
                return 1
        if 0 <= j + 2 < 5:
            if board[i][j + 1] == 1 and board[i][j + 2] == 1:
                return 1
        return 0

    def check_defensive_shapes(self, board, i, j):
        liberties = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= i + dx < 5 and 0 <= j + dy < 5:
                if board[i + dx][j + dy] == 0:
                    liberties += 1
        if liberties == 1:
            return 1
        return 0

    def is_eye_shape(self, board, i, j, piece_type):
        if board[i][j] != 0:
            return False

        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + x, j + y
            if 0 <= ni < 5 and 0 <= nj < 5 and board[ni][nj] != piece_type:
                return False
        return True


    def evaluate_shape(self, board, piece_type):
        score = 0
        patterns = {
            "live_four": [[piece_type, piece_type, piece_type, piece_type, 0]],
            "dead_four": [[self.opponent(piece_type), piece_type, piece_type, piece_type, 0]],
            "live_three": [[piece_type, piece_type, piece_type, 0, 0]],
        }

        pattern_scores = {
            "live_four": 3,
            "dead_four": -1,
            "live_three": 2,
        }

        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.is_eye_shape(board, i, j, piece_type):
                    score += 4
                for pattern_name, pattern in patterns.items():
                    if self.match_pattern(board, i, j, pattern):
                        score += pattern_scores[pattern_name]

        return score

    def match_pattern(self, board, x, y, pattern):
        if x + len(pattern) > len(board) or y + len(pattern[0]) > len(board[0]):
            return False

        for i in range(len(pattern)):
            for j in range(len(pattern[0])):
                if pattern[i][j] != 0 and pattern[i][j] != board[x + i][y + j]:
                    return False
        return True
    def evaluate_board(self, go, cur_player, piece_type):
        base_score = go.score(piece_type) - go.score(self.opponent(piece_type))
        sign_modifier = 1 if piece_type == 1 else -1
        base_modifier = -2.5 if cur_player == 0 else 2.5
        score = base_score + sign_modifier * base_modifier
        score += sign_modifier * self.evaluate_shape(go.board, piece_type)
        return score
    def count_liberties(self, board, i, j, piece_type, visited=None):
        if visited is None:
            visited = set()
        if not self.is_valid_position(i, j) or (i, j) in visited:
            return 0
        if board[i][j] == 0:
            return 1
        if board[i][j] == self.opponent(piece_type):
            return 0
        visited.add((i, j))

        neighbors = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        total_liberties = sum(self.count_liberties(board, x, y, piece_type, visited) for x, y in neighbors)

        return total_liberties

    def is_valid_position(self, i, j):
        return 0 <= i < 5 and 0 <= j < 5

    def get_chain_liberties(self, board, i, j, visited=None):
        if visited is None:
            visited = set()

        if (i, j) in visited or board[i][j] == 0:
            return set()

        visited.add((i, j))
        piece_type = board[i][j]
        liberties = set()

        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + x, j + y
            if 0 <= ni < 5 and 0 <= nj < 5:
                if board[ni][nj] == 0:
                    liberties.add((ni, nj))
                elif board[ni][nj] == piece_type:
                    liberties |= self.get_chain_liberties(board, ni, nj, visited)

        return liberties

    def total_chain_liberties(self, board, piece_type):
        visited = set()
        total_liberties = 0

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == piece_type and (i, j) not in visited:
                    chain_liberties = self.get_chain_liberties(board, i, j, set())
                    total_liberties += len(chain_liberties)
                    visited.update(chain_liberties)

        return total_liberties


    def all_chain_liberties(self, board, piece_type):
        visited = set()
        chains_liberties = {}

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == piece_type and (i, j) not in visited:
                    chain_liberties = self.get_chain_liberties(board, i, j, set())
                    chains_liberties[(i, j)] = len(chain_liberties)
                    visited.update(chain_liberties)

        return chains_liberties

    def pieces_with_one_liberty(self, board, piece_type):
        visited = set()
        count = 0

        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                position = (i, j)

                if piece == piece_type and position not in visited:
                    if self.count_liberties(board, i, j, piece_type, set()) == 1:
                        count += 1
                        visited.add(position)

        return count

    def can_merge_chains(self, board, i, j, piece_type):
        # 检查是否在此位置放置一个子后，存在两个相邻的相同颜色的链条
        if board[i][j] != 0:
            return False

        visited = set()
        adj_chains = 0

        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + x, j + y
            if 0 <= ni < 5 and 0 <= nj < 5 and board[ni][nj] == piece_type:
                chain_liberties = self.get_chain_liberties(board, ni, nj, set())
                if len(chain_liberties) > 1:  # 如果该链条已经有超过1的自由度，那么放置此位置的子对合并链条没有帮助
                    continue
                adj_chains += 1
                visited.update(chain_liberties)

        return adj_chains > 1

    def min_max_ab_pruning(self, go, cur_player, piece_type, alpha, beta, depth):
        board_hash = self.compute_hash(go.board)
        if board_hash in self.transposition_table:
            stored_value, stored_depth = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return [None, stored_value]

        if piece_type == 1:
            factor = 3
            # be_factor = 3
        else:
            factor = 3
            # be_factor = 3

        if depth > 4:
            return [None, self.evaluate_board(go, cur_player, piece_type)]

        best_move = None
        if cur_player == 0:
            max_eval = -math.inf
        else:
            max_eval = math.inf

        for move in self.heuristic_move_order(go, piece_type):
            if go.valid_place_check(*move, piece_type):
                new_go = deepcopy(go)
                new_go.place_chess(*move, piece_type)
                captured_pieces_count = len(new_go.remove_died_pieces(self.opponent(piece_type)))
                # be_captured_pieces_count = len(new_go.remove_died_pieces(piece_type))
                _, score = self.min_max_ab_pruning(new_go, 1 - cur_player, self.opponent(piece_type), alpha, beta, depth + 1)
                if self.can_merge_chains(new_go.board, *move, piece_type):
                    merge_bonus = 5
                else:
                    merge_bonus = 0
                threatened_pieces_score = 2 * self.pieces_with_one_liberty(new_go.board, piece_type)
                opponent_threatened_pieces_score = 0 * self.pieces_with_one_liberty(new_go.board, self.opponent(piece_type))
                my_chain_liberties = self.total_chain_liberties(new_go.board, piece_type)
                opp_chain_liberties = self.total_chain_liberties(new_go.board, self.opponent(piece_type))
                chain_liberties_diff = my_chain_liberties - opp_chain_liberties
                if cur_player == 0:
                    final_score = score + factor * captured_pieces_count - threatened_pieces_score + opponent_threatened_pieces_score + chain_liberties_diff * 3 + new_go.score(
                        piece_type) - new_go.score(self.opponent(piece_type)) + merge_bonus * 0
                    if final_score > max_eval:
                        max_eval, best_move = final_score, move
                        alpha = max(alpha, final_score)
                else:
                    final_score = score - factor * captured_pieces_count + threatened_pieces_score - opponent_threatened_pieces_score - chain_liberties_diff * 3 + new_go.score(
                        self.opponent(piece_type)) - new_go.score(piece_type) - merge_bonus * 0
                    if final_score < max_eval:
                        max_eval, best_move = final_score, move
                        beta = min(beta, final_score)

                if beta <= alpha:
                    break
        self.transposition_table[board_hash] = (max_eval, depth)
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


