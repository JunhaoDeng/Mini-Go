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
        self.transposition_table = {}
        self.zobrist_table = self.init_zobrist()

    def opponent(self, piece_type):
        return 3 - piece_type

    def init_zobrist(self):
        import random
        table = {}
        for i in range(5):
            for j in range(5):
                for k in [1, 2]:  # for each piece type
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
        """
        Return a list of moves ordered by heuristic value.
        """
        moves_heuristic = {}

        # Calculate heuristic for each move
        for move in self.move_order:
            if go.valid_place_check(*move, piece_type):
                heuristic_val = self.calculate_heuristic(go, move, piece_type)
                moves_heuristic[tuple(move)] = heuristic_val

        # Sort moves by heuristic value, in descending order for maximizing player
        sorted_moves = sorted(moves_heuristic, key=moves_heuristic.get, reverse=True)

        # Return sorted moves
        return sorted_moves

    def calculate_heuristic(self, go, move, piece_type):
        """
        Calculate heuristic value for a given move.
        The exact computation can be more sophisticated based on game knowledge.
        For simplicity, we will just use evaluate_board function.
        """
        new_go = deepcopy(go)
        new_go.place_chess(*move, piece_type)
        new_go.remove_died_pieces(self.opponent(piece_type))
        heuristic_val = self.evaluate_board(new_go, 0, piece_type)

        return heuristic_val

    def is_eye_shape(self, board, i, j, piece_type):
        """检查某位置是否为眼"""
        if board[i][j] != 0:
            return False

        for x, y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni, nj = i + x, j + y
            if 0 <= ni < 5 and 0 <= nj < 5 and board[ni][nj] != piece_type:
                return False
        return True


    def evaluate_shape(self, board, piece_type):
        score = 0
        # Example patterns:
        # Note: These are not real Go patterns but just an example to show the structure
        patterns = {
            "live_four": [[piece_type, piece_type, piece_type, piece_type, 0]],
            "dead_four": [[self.opponent(piece_type), piece_type, piece_type, piece_type, 0]],
            "live_three": [[piece_type, piece_type, piece_type, 0, 0]],
            # ... Add more patterns as needed
        }

        pattern_scores = {
            "live_four": 3,
            "dead_four": -1,
            "live_three": 2,
            # ... Assign scores to other patterns
        }

        # Loop through the board and search for patterns
        for i in range(len(board)):
            for j in range(len(board[0])):
                if self.is_eye_shape(board, i, j, piece_type):
                    score += 4  # 为眼形状加4分
                for pattern_name, pattern in patterns.items():
                    if self.match_pattern(board, i, j, pattern):
                        score += pattern_scores[pattern_name]

        return score

    def match_pattern(self, board, x, y, pattern):
        """
        Check if the given pattern matches the board starting at position (x, y).
        """
        if x + len(pattern) > len(board) or y + len(pattern[0]) > len(board[0]):
            return False

        for i in range(len(pattern)):
            for j in range(len(pattern[0])):
                if pattern[i][j] != 0 and pattern[i][j] != board[x + i][y + j]:
                    return False
        return True

    # def evaluate_board(self, go, cur_player, piece_type):
    #     if cur_player == 0:
    #         base_score = go.score(1) - go.score(2)
    #         if piece_type == 1:
    #             score = base_score - 2.5
    #         else:
    #             score = base_score + 2.5
    #     else:
    #         base_score = go.score(2) - go.score(1)
    #         if piece_type == 1:
    #             score = base_score + 2.5
    #         else:
    #             score = base_score - 2.5
    #     shape_score = self.evaluate_shape(go.board, piece_type)
    #     if cur_player == 0:
    #         if piece_type == 1:
    #             score += shape_score
    #         else:
    #             score -= shape_score
    #     else:
    #         if piece_type == 1:
    #             score -= shape_score
    #         else:
    #             score += shape_score
    #     return score

    def evaluate_board(self, go, cur_player, piece_type):
        base_score = go.score(piece_type) - go.score(self.opponent(piece_type))
        sign_modifier = 1 if piece_type == 1 else -1
        base_modifier = -2.5 if cur_player == 0 else 2.5
        score = base_score + sign_modifier * base_modifier

        # Incorporate the shape evaluation
        score += sign_modifier * self.evaluate_shape(go.board, piece_type)

        # Consider chain liberties
        # visited = set()
        # for i in range(5):
        #     for j in range(5):
        #         if go.board[i][j] == piece_type and (i, j) not in visited:
        #             liberties = len(self.get_chain_liberties(go.board, i, j))
        #             score += sign_modifier * liberties * 0.5  # tweak this multiplier as necessary

        return score

    def count_liberties(self, board, i, j, piece_type, visited=None):
        """
        Count the number of liberties for a piece on the board.
        """
        if visited is None:
            visited = set()

        if not self.is_valid_position(i, j) or (i, j) in visited:
            return 0

        # If it's an empty spot, it's a liberty
        if board[i][j] == 0:
            return 1

        # If it's an opponent's piece, it's not a liberty
        if board[i][j] == self.opponent(piece_type):
            return 0

        visited.add((i, j))

        # For each neighboring spot, check for liberties recursively
        neighbors = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
        total_liberties = sum(self.count_liberties(board, x, y, piece_type, visited) for x, y in neighbors)

        return total_liberties

    def is_valid_position(self, i, j):
        """
        Check if the given position is inside the board.
        """
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
        """
        Count the total number of chain liberties for all chains of the given piece_type.
        """
        visited = set()
        total_liberties = 0

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == piece_type and (i, j) not in visited:
                    chain_liberties = self.get_chain_liberties(board, i, j, set())
                    total_liberties += len(chain_liberties)
                    visited.update(chain_liberties)

        return total_liberties

    def pieces_with_one_liberty(self, board, piece_type):
        """
        Count the number of pieces of a given type with only one liberty.
        """
        visited = set()
        count = 0

        # Go through each position on the board
        for i, row in enumerate(board):
            for j, piece in enumerate(row):
                position = (i, j)

                if piece == piece_type and position not in visited:
                    if self.count_liberties(board, i, j, piece_type, set()) == 1:
                        count += 1
                        visited.add(position)

        return count

    # def pieces_with_one_liberty(self, board, piece_type):
    #     visited = set()
    #     count = 0
    #     for i in range(len(board)):
    #         for j in range(len(board[0])):
    #             if board[i][j] == piece_type and str(i) + str(j) not in visited:
    #                 if self.count_liberties(board, i, j, piece_type, set()) == 1:
    #                     count += 1
    #     return count

    def min_max_ab_pruning(self, go, cur_player, piece_type, alpha, beta, depth):
        # Check the transposition table first
        board_hash = self.compute_hash(go.board)
        if board_hash in self.transposition_table:
            stored_value, stored_depth = self.transposition_table[board_hash]
            if stored_depth >= depth:
                return [None, stored_value]

        if depth > 3:
            return [None, self.evaluate_board(go, cur_player, piece_type)]

        best_move = None
        if cur_player == 0:
            max_eval = -math.inf
        else:
            max_eval = math.inf

        # 使用启发式排序
        for move in self.heuristic_move_order(go, piece_type):
            if go.valid_place_check(*move, piece_type):
                new_go = deepcopy(go)
                new_go.place_chess(*move, piece_type)
                captured_pieces_count = len(new_go.remove_died_pieces(self.opponent(piece_type)))
                _, score = self.min_max_ab_pruning(new_go, 1 - cur_player, self.opponent(piece_type), alpha, beta, depth + 1)

                threatened_pieces_score = 2 * self.pieces_with_one_liberty(new_go.board, piece_type)
                # New code: Add chain liberties to the heuristic
                my_chain_liberties = self.total_chain_liberties(new_go.board, piece_type)
                opp_chain_liberties = self.total_chain_liberties(new_go.board, self.opponent(piece_type))
                chain_liberties_diff = my_chain_liberties - opp_chain_liberties
                if cur_player == 0:
                    final_score = score + 3 * captured_pieces_count - threatened_pieces_score + chain_liberties_diff + new_go.score(
                        piece_type) - new_go.score(self.opponent(piece_type))
                    if final_score > max_eval:
                        max_eval, best_move = final_score, move
                        alpha = max(alpha, final_score)
                else:
                    final_score = score - 3 * captured_pieces_count + threatened_pieces_score - chain_liberties_diff  + new_go.score(
                        self.opponent(piece_type)) - new_go.score(piece_type)
                    if final_score < max_eval:
                        max_eval, best_move = final_score, move
                        beta = min(beta, final_score)

                if beta <= alpha:
                    break

        # Store the result in the transposition table
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
    # # Use MCTS to get the best action
    # action = player.get_input_mcts(go, piece_type)
    writeOutput(action)


