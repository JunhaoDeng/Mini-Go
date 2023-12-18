import math
from copy import deepcopy
from read import readInput
from write import writeOutput
from host import GO
import numpy as np

class QLearning:
    def __init__(self, learning_rate=0.01, discount_factor=0.9, exploration_rate=0.5, exploration_decay=0.995):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.q_table = {}
        self.previous_board = None
        self.previous_action = None

    def get_q_value(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, available_actions, current_board):
        if np.random.uniform(0, 1) < self.exploration_rate:
            return np.random.choice(available_actions)
        q_values = [self.get_q_value(current_board, action) for action in available_actions]
        return available_actions[np.argmax(q_values)]

    def learn(self, old_state, action, reward, new_state):
        old_q_value = self.get_q_value(old_state, action)
        max_future_q = max([self.get_q_value(new_state, act) for act in new_state.get_available_actions()])
        new_q_value = old_q_value + self.learning_rate * (reward + self.discount_factor * max_future_q - old_q_value)
        self.q_table[(old_state, action)] = new_q_value

    def learn_from_minmax(self, old_state, minmax_action, new_state, reward):
        self.learn(old_state, minmax_action, reward, new_state)

    def update_exploration(self):
        self.exploration_rate *= self.exploration_decay



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

        # Additional Heuristics based on distance and shapes
        heuristic_val -= self.distance_to_center(*move)
        heuristic_val += self.check_aggressive_shapes(new_go.board, *move)
        heuristic_val -= self.check_defensive_shapes(new_go.board, *move)

        return heuristic_val

    def distance_to_center(self, i, j):
        center = 2
        return abs(i - center) + abs(j - center)

    def check_aggressive_shapes(self, board, i, j):
        # Checking for simple shapes in a 5x5 board
        if 0 <= i + 2 < 5:
            if board[i + 1][j] == 1 and board[i + 2][j] == 1:
                return 1  # Detected a shape, return a bonus
        if 0 <= j + 2 < 5:
            if board[i][j + 1] == 1 and board[i][j + 2] == 1:
                return 1  # Detected a shape, return a bonus
        return 0  # No aggressive shape detected

    def check_defensive_shapes(self, board, i, j):
        liberties = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            if 0 <= i + dx < 5 and 0 <= j + dy < 5:
                if board[i + dx][j + dy] == 0:  # Empty intersection, so a liberty
                    liberties += 1
        if liberties == 1:
            return 1  # Stone at (i, j) has only one liberty, return a penalty
        return 0  # Otherwise, no penalty

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
                    score += 4  # 为眼形状加4分
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

    def min_max_ab_pruning(self, go, cur_player, piece_type, alpha, beta, depth):
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

        for move in self.heuristic_move_order(go, piece_type):
            if go.valid_place_check(*move, piece_type):
                new_go = deepcopy(go)
                new_go.place_chess(*move, piece_type)
                captured_pieces_count = len(new_go.remove_died_pieces(self.opponent(piece_type)))
                _, score = self.min_max_ab_pruning(new_go, 1 - cur_player, self.opponent(piece_type), alpha, beta, depth + 1)
                threatened_pieces_score = 2 * self.pieces_with_one_liberty(new_go.board, piece_type)
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

        self.transposition_table[board_hash] = (max_eval, depth)

        return best_move, max_eval

    def get_input(self, go, piece_type):
        next_move, _ = self.min_max_ab_pruning(go, 0, piece_type, -math.inf, math.inf, 1)
        if next_move is None:
            next_move = "PASS"
        return next_move


class CombinedAgent:
    def __init__(self):
        self.ql = QLearning()
        self.mm = MinMaxPlayer()

    def get_valid_moves(self, board, go, piece_type):
        valid_moves = []
        for x in range(len(board)):
            for y in range(len(board[0])):
                if board[x][y] == 0:  # assuming 0 represents an empty spot
                    temp_board = deepcopy(board)
                    temp_board[x][y] = piece_type
                    if go.valid_place_check(x, y, piece_type):
                        valid_moves.append((x, y))
        return valid_moves

    def get_action(self, go, piece_type):
        # Step 1: Use MinMax to get the best action
        best_move, _ = self.mm.min_max_ab_pruning(go, 0, piece_type, -math.inf, math.inf, 1)

        if best_move is None:
            best_move = "PASS"

        # Step 2: Use Q-learning to decide whether to follow MinMax's action or explore
        available_actions = self.get_valid_moves(go.board, go, piece_type)
        chosen_action = self.ql.choose_action(available_actions, go.board)

        # Use MinMax action if Q-learning chooses to exploit, otherwise explore
        if chosen_action == best_move or best_move == "PASS":
            final_action = best_move
        else:
            final_action = chosen_action

        # Update Q-learning based on MinMax's recommendation
        if self.ql.previous_board is not None and self.ql.previous_action is not None:
            reward = go.score(piece_type) - go.score(
                3 - piece_type)  # the difference in score can be considered as a reward
            self.ql.learn_from_minmax(self.ql.previous_board, self.ql.previous_action, go.board, reward)

        # Update Q-learning's state
        self.ql.previous_board = deepcopy(go.board)
        self.ql.previous_action = final_action
        self.ql.update_exploration()

        return final_action

    def update_exploration(self):
        self.ql.update_exploration()

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
    # n = 5
    # try:
    #     input = readInput(n)
    #     piece_type, previous_board, board = input
    # except:
    #     piece_type, previous_board, board = 1, None, None
    # go = GO(n)
    # go.set_board(piece_type, previous_board, board)
    # agent = CombinedAgent()
    # action = agent.get_action(go, piece_type)
    # writeOutput(action)

