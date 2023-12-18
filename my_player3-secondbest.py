import math
from copy import deepcopy
from read import readInput
from write import writeOutput
from host import GO
from collections import deque

class MinMaxPlayer:
    def __init__(self):
        self.move_order = [[2, 2], [1, 1], [1, 3], [0, 2], [3, 3], [2, 4], [3, 1], [4, 2], [2, 0],
                           [0, 0], [0, 1], [2, 3], [0, 3], [0, 4], [1, 4], [2, 1], [3, 4], [4, 4],
                           [4, 3], [1, 0], [4, 1], [4, 0], [3, 0], [1, 2], [3, 2]]
        self.transposition_table = {}

    def store_in_transposition_table(self, board_hash, value):
        self.transposition_table[board_hash] = value

    def retrieve_from_transposition_table(self, board_hash):
        return self.transposition_table.get(board_hash, None)

    def board_to_hash(self, board):
        return str(board)

    def order_moves(self, go, piece_type):
        def heuristic(move):
            new_go = deepcopy(go)
            new_go.place_chess(*move, piece_type)
            return -len(new_go.remove_died_pieces(3 - piece_type))

        return sorted(self.move_order, key=heuristic, reverse=True)

    def evaluate_board(self, go, cur_player, piece_type):
        base_score = 0
        center_bonus = [(2, 2), (2, 1), (2, 3), (1, 2), (3, 2)]
        for i in range(5):
            for j in range(5):
                # 1. 加权角落和边界的得分
                multiplier = 1.5 if i in [0, 4] and j in [0, 4] else 1.1 if i in [0, 4] or j in [0, 4] else 1

                # 黑子中心控制加分
                if piece_type == 1 and (i, j) in center_bonus:
                    multiplier += 0.5

                if go.board[i][j] == piece_type:
                    base_score += multiplier
                elif go.board[i][j] == 3 - piece_type:
                    base_score -= multiplier

                # 2. 考虑棋子的活气
                visited_piece = set()
                if go.board[i][j] == piece_type:
                    liberty = self.count_liberties(go.board, i, j, piece_type, visited_piece)
                    base_score += liberty

                visited_opponent = set()
                if go.board[i][j] == 3 - piece_type:
                    liberty = self.count_liberties(go.board, i, j, 3 - piece_type, visited_opponent)
                    base_score -= liberty

        # 3. 考虑棋形
        # base_score += self.evaluate_shapes(go.board, piece_type)

        # 4. 考虑“活一”的情况
        # base_score -= 3 * self.pieces_with_one_liberty(go.board, piece_type)
        # base_score += 3 * self.pieces_with_one_liberty(go.board, 3 - piece_type)

        if cur_player == 0:
            if piece_type == 1:
                score = base_score - 2.5
            else:
                score = base_score + 2.5
        else:
            if piece_type == 1:
                score = base_score + 2.5
            else:
                score = base_score - 2.5

        return score

    def evaluate_shapes(self, board, piece_type):
        score = 0

        # 定义各种棋形的模式和分数
        shapes = {
            # 'live_two': ['0010', '0100'],
            'live_three': ['0110', '01010', '010010'],
            'dead_three': ['2110', '21010', '210010', '0112', '01012', '010012'],
            'live_four': ['01110'],
            'dead_four': ['21110', '01112', '11012'],
            # 可以添加更多的棋型
        }

        scores = {
            'single_liberty': -700, # 增加风险
            'double_liberty': -300, # 提高评分
            'healthy': 250,         # 轻微调整
            'eye': 450,
            # 'single_liberty': 0,  # 增加风险
            # 'double_liberty': 0,  # 提高评分
            # 'healthy': 0,  # 轻微调整
            # 'eye': 450,
            'live_two': 300,
            'live_three': 600,
            'dead_three': -600,
            'live_four': 1200,
            'dead_four': -1200,
            # 对分数进行细致的调整
        }

        visited = set()  # 用于标记已经访问过的棋子

        for x in range(5):
            for y in range(5):
                if (x, y) not in visited and board[x][y] == piece_type:
                    liberties = self.count_liberties(board, x, y, piece_type, visited)

                    # 基于气的数量进行评分
                    if liberties == 1:
                        score += scores['single_liberty']
                    elif liberties == 2:
                        score += scores['double_liberty']
                    else:
                        score += scores['healthy']

                    # 如果形成眼，加分
                    if self.is_eye(board, x, y, piece_type):
                        score += scores['eye']

                    # 检查棋形并评分
                    # 水平
                    if y <= 1:
                        shape = ''.join(map(str, board[x][y:y + 4]))
                        for s, patterns in shapes.items():
                            if shape in patterns:
                                score += scores[s]

                    # 垂直
                    if x <= 1:
                        shape = ''.join(map(str, [board[x + i][y] for i in range(4)]))
                        for s, patterns in shapes.items():
                            if shape in patterns:
                                score += scores[s]

                    # 主对角线
                    if x <= 1 and y <= 1:
                        shape = ''.join(map(str, [board[x + i][y + i] for i in range(4)]))
                        for s, patterns in shapes.items():
                            if shape in patterns:
                                score += scores[s]

                    # 副对角线
                    if x >= 3 and y <= 1:
                        shape = ''.join(map(str, [board[x - i][y + i] for i in range(4)]))
                        for s, patterns in shapes.items():
                            if shape in patterns:
                                score += scores[s]

        return score

    def is_eye(self, board, x, y, piece_type):
        # 基于5x5棋盘，此处仅为简化的眼检测逻辑
        if board[x][y] != 0:
            return False
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 5 and 0 <= ny < 5 and board[nx][ny] != piece_type:
                return False
        return True

    def count_liberties(self, board, x, y, piece_type, visited):
        # 修改count_liberties以更新访问过的棋子集合
        queue = deque([(x, y)])
        visited.add((x, y))
        liberties = 0

        while queue:
            cx, cy = queue.popleft()

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < 5 and 0 <= ny < 5:
                    if board[nx][ny] == 0:
                        liberties += 1
                    elif board[nx][ny] == piece_type and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))

        return liberties

    def pieces_with_one_liberty(self, board, piece_type):
        count = 0

        for i in range(5):
            for j in range(5):
                if board[i][j] == piece_type:
                    visited = set()
                    if self.count_liberties(board, i, j, piece_type, visited) == 1:
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

        # Transposition Table Retrieval
        current_hash = self.board_to_hash(go.board)
        cached_result = self.retrieve_from_transposition_table(current_hash)
        if cached_result:
            return cached_result

        # Use our move ordering
        ordered_moves = self.order_moves(go, piece_type)
        for move in ordered_moves:
            if go.valid_place_check(*move, piece_type):
                new_go = deepcopy(go)
                new_go.place_chess(*move, piece_type)
                eat_num = len(new_go.remove_died_pieces(3 - piece_type))
                _, score = self.min_max_ab_pruning(new_go, 1 - cur_player, 3 - piece_type, alpha, beta, depth + 1)

                endangered_score = 2 * self.pieces_with_one_liberty(new_go.board, piece_type)
                if cur_player == 0:
                    final_score = score + 3 * eat_num - endangered_score + new_go.score(piece_type) - new_go.score(
                        3 - piece_type)
                    if final_score > max_eval:
                        max_eval, best_move = final_score, move
                        alpha = max(alpha, final_score)
                else:
                    final_score = score - 3 * eat_num + endangered_score + new_go.score(3 - piece_type) - new_go.score(
                        piece_type)
                    if final_score < max_eval:
                        max_eval, best_move = final_score, move
                        beta = min(beta, final_score)

                if beta <= alpha:
                    break

        # Store in transposition table
        self.store_in_transposition_table(current_hash, (best_move, max_eval))
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
