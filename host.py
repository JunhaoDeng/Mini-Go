import sys

import argparse
from copy import deepcopy

from read import *
from write import writeNextInput


class GO:
    def __init__(self, n):
        """
        Go game.

        :param n: size of the board n*n
        """
        self.size = n
        # self.previous_board = None # Store the previous board
        self.X_move = True  # X chess plays first
        '''在初始化对象时就设置好了，不是接受的参数'''
        self.died_pieces = []  # Intialize died pieces to be empty
        self.n_move = 0  # Trace the number of moves
        '''目前是第几手'''
        self.max_move = n * n - 1  # The max movement of a Go game
        '''最大手数在这就设置好了，不是接受的参数'''
        self.komi = n / 2  # Komi rule
        '''在初始化对象时就设置好了，不是接受的参数'''
        self.verbose = False
        '''人下:True, 程序下：False; Verbose only when there is a manual player'''

    def init_board(self, n):
        '''
        self.board = n*n个0的二维数组
        self.previous_board 也 = n*n个0的二维数组
        Initialize a board with size n*n.

        :param n: width and height of the board.
        :return: None.
        '''
        board = [[0 for x in range(n)] for y in range(n)]  # Empty space marked as 0
        # 'X' pieces marked as 1
        # 'O' pieces marked as 2
        # 初始的时候，pre
        self.board = board
        self.previous_board = deepcopy(board)

    def set_board(self, piece_type, previous_board, board):
        '''
        先提了死子，然后把棋盘给self.
        Initialize board status.
        :param previous_board: previous board state.
        :param board: current board state.
        :return: None.
        '''

        # 'X' pieces marked as 1
        # 'O' pieces marked as 2

        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))

        # self.piece_type = piece_type
        self.previous_board = previous_board
        self.board = board

    def ifTwoBoardSame(self, board1, board2):
        '''
        比较两个棋盘是不是一样，一样True，不一样False
        :param board1:
        :param board2:
        :return:
        '''
        for i in range(self.size):
            for j in range(self.size):
                if board1[i][j] != board2[i][j]:
                    return False
        return True

    def copy_board(self):
        '''
        返回的是一个go对象
        Copy the current board for potential testing.

        :param: None.
        :return: the copied board instance.
        '''
        return deepcopy(self)

    def detect_neighbor(self, i, j):
        '''
        返回一个棋子相邻的坐标（中间四个，边三个，角两个）
        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbors row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = []
        # Detect borders and add neighbor coordinates
        if i > 0: neighbors.append((i - 1, j))
        if i < len(board) - 1: neighbors.append((i + 1, j))
        if j > 0: neighbors.append((i, j - 1))
        if j < len(board) - 1: neighbors.append((i, j + 1))
        return neighbors

    def detect_neighbor_ally(self, i, j):
        '''
        只返回相邻的友军，就算是一大片友军连在一块，也最多返回四个
        Detect the neighbor allies of a given stone.
        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the neighbored allies row and column (row, column) of position (i, j).
        '''
        board = self.board
        neighbors = self.detect_neighbor(i, j)  # Detect neighbors
        group_allies = []
        # Iterate through neighbors
        for piece in neighbors:
            # Add to allies list if having the same color
            if board[piece[0]][piece[1]] == board[i][j]:
                group_allies.append(piece)
        return group_allies

    def ally_dfs(self, i, j):
        '''
        返回与这个棋子相连的所有的友军，包括他自己
        Using DFS to search for all allies of a given stone.
        :param i: row number of the board.
        :param j: column number of the board.
        :return: a list containing the all allies row and column (row, column) of position (i, j).
        '''
        stack = [(i, j)]  # stack for DFS serach
        ally_members = []  # record allies positions during the search
        while stack:
            piece = stack.pop()
            ally_members.append(piece)
            neighbor_allies = self.detect_neighbor_ally(piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in stack and ally not in ally_members:
                    stack.append(ally)
        return ally_members

    def find_liberty(self, i, j):
        '''
        返回的是这块棋有没有气，有气返回True，无气返回False
        Find liberty of a given stone. If a group of allied stones has no liberty, they all die.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: boolean indicating whether the given stone still has liberty.
        '''
        board = self.board
        ally_members = self.ally_dfs(i, j)
        for member in ally_members:
            neighbors = self.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    return True
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return False

    def find_died_pieces(self, piece_type):
        '''
        返回一个由死棋坐标构成的数组
        Find the died stones that has no liberty in the board for a given piece type.

        :param piece_type: 1('X') or 2('O').
        :return: a list containing the dead pieces row and column(row, column).
        '''
        board = self.board
        died_pieces = []

        for i in range(len(board)):
            for j in range(len(board)):
                # Check if there is a piece at this position:
                if board[i][j] == piece_type:
                    # The piece die if it has no liberty
                    if not self.find_liberty(i, j):
                        died_pieces.append((i, j))
        return died_pieces

    def remove_died_pieces(self, piece_type):
        '''
        把piece_type的死子都设置为0
        Remove the dead stones in the board.

        :param piece_type: 1('X') or 2('O').
        :return: locations of dead pieces.
        '''

        died_pieces = self.find_died_pieces(piece_type)
        if not died_pieces: return []
        self.remove_certain_pieces(died_pieces)
        return died_pieces

    def remove_certain_pieces(self, positions):
        '''
        把这个位置的棋子提掉（设置为0）

        :param positions: a list containing the pieces to be removed row and column(row, column)
        :return: None.
        '''
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.update_board(board)

    def place_chess(self, i, j, piece_type):
        """
        尝试把i,j的符号改成piece_type，并且修改了previous board和board为，此手之前和此手之后的棋盘
        对方就知道你下在哪了
        Place a chess stone in the board.
        param i: row number of the board.
        param j: column number of the board.
        param piece_type: 1('X') or 2('O').
        return boolean indicating whether the placement is valid.
        """
        board = self.board

        valid_place = self.valid_place_check(i, j, piece_type)
        if not valid_place:
            return False
        self.previous_board = deepcopy(board)
        board[i][j] = piece_type
        self.update_board(board)
        # Remove the following line for HW2 CS561 S2020
        # self.n_move += 1
        return True

    def valid_place_check(self, i, j, piece_type, test_check=False):
        '''
        检测落点是否有效：是否在棋盘范围内；这个位置是否已经有子了；下在这是不是会自杀；是不是在老打一个劫；只是检测，不会改棋盘
        Check whether a placement is valid.

        :param i: row number of the board.
        :param j: column number of the board.
        :param piece_type: 1(white piece) or 2(black piece).
        :param test_check: boolean if it's a test check.
        :return: boolean indicating whether the placement is valid.
        '''
        board = self.board
        verbose = self.verbose
        if test_check:
            verbose = False

        # Check if the place is in the board range
        if not (i >= 0 and i < len(board)):
            if verbose:
                print(('Invalid placement. row should be in the range 1 to {}.').format(len(board) - 1))
            return False
        if not (j >= 0 and j < len(board)):
            if verbose:
                print(('Invalid placement. column should be in the range 1 to {}.').format(len(board) - 1))
            return False

        # Check if the place already has a piece
        if board[i][j] != 0:
            if verbose:
                print('Invalid placement. There is already a chess in this position.')
            return False

        # Copy the board for testing
        # 把自己重新拷贝了一分（不只是棋盘）
        test_go = self.copy_board()
        test_board = test_go.board

        # Check if the place has liberty
        # 如果下进去还有气，那随便下
        test_board[i][j] = piece_type
        test_go.update_board(test_board)
        if test_go.find_liberty(i, j):
            return True

        # If not, remove the died pieces of opponent and check again
        # 下进去没气，看看是不是吃对手的棋
        test_go.remove_died_pieces(3 - piece_type)
        # 提子了，还是没气，那就不能下
        if not test_go.find_liberty(i, j):
            if verbose:
                print('Invalid placement. No liberty found in this position.')
            return False

        # Check special case: repeat placement causing the repeat board state (KO rule)
        else:
            # 提子了，有气，那看看是不是打劫，是的话也不行。
            if self.died_pieces and self.ifTwoBoardSame(self.previous_board, test_go.board):
                if verbose:
                    print('Invalid placement. A repeat move not permitted by the KO rule.')
                return False
        return True

    def update_board(self, new_board):
        '''
        直接给你换张棋盘
        Update the board with new_board

        :param new_board: new board.
        :return: None.
        '''
        self.board = new_board

    def visualize_board(self):
        '''
        把棋盘打印到命令行
        Visualize the board.

        :return: None
        '''
        board = self.board

        print('-' * len(board) * 2)
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    print(' ', end=' ')
                elif board[i][j] == 1:
                    print('X', end=' ')
                else:
                    print('O', end=' ')
            print()
        print('-' * len(board) * 2)

    def game_end(self, piece_type, action="MOVE"):
        '''
        超过最多步数/连续两张棋盘一样，并且上一步是PASS
        Check if the game should end.

        :param piece_type: 1('X') or 2('O').
        :param action: "MOVE" or "PASS".
        :return: boolean indicating whether the game should end.
        '''

        # Case 1: max move reached
        if self.n_move >= self.max_move:
            return True
        # Case 2: two players all pass the move.
        if self.ifTwoBoardSame(self.previous_board, self.board) and action == "PASS":
            return True
        return False

    def score(self, piece_type):
        '''
        返回棋盘上有多少piece_type的子
        Get score of a player by counting the number of stones.

        :param piece_type: 1('X') or 2('O').
        :return: boolean indicating whether the game should end.
        '''

        board = self.board
        cnt = 0
        for i in range(self.size):
            for j in range(self.size):
                if board[i][j] == piece_type:
                    cnt += 1
        return cnt

    def judge_winner(self):
        '''
        返回1赢/2赢/0平局
        Judge the winner of the game by number of pieces for each player.

        :param: None.
        :return: piece type of winner of the game (0 if it's a tie).
        '''

        cnt_1 = self.score(1)
        cnt_2 = self.score(2)
        if cnt_1 > cnt_2 + self.komi:
            return 1
        elif cnt_1 < cnt_2 + self.komi:
            return 2
        else:
            return 0

    def play(self, player1, player2, verbose=False):
        '''
        The game starts!

        :param player1: Player instance.
        :param player2: Player instance.
        :param verbose: whether print input hint and error information
        :return: piece type of winner of the game (0 if it's a tie).
        '''
        self.init_board(self.size)
        # Print input hints and error message if there is a manual player
        # 看看是不是手动下棋
        if player1.type == 'manual' or player2.type == 'manual':
            self.verbose = True
            print('----------Input "exit" to exit the program----------')
            print('X stands for black chess, O stands for white chess.')
            self.visualize_board()

        verbose = self.verbose
        # Game starts!
        while 1:
            piece_type = 1 if self.X_move else 2

            # Judge if the game should end
            if self.game_end(piece_type):
                result = self.judge_winner()
                if verbose:
                    print('Game ended.')
                    if result == 0:
                        print('The game is a tie.')
                    else:
                        print('The winner is {}'.format('X' if result == 1 else 'O'))
                return result

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(player + " makes move...")

            # Game continues
            if piece_type == 1:
                action = player1.minMaxABCut(self, piece_type)
            else:
                action = player2.minMaxABCut(self, piece_type)

            if verbose:
                player = "X" if piece_type == 1 else "O"
                print(action)

            if action != "PASS":
                # If invalid input, continue the loop. Else it places a chess on the board.
                if not self.place_chess(action[0], action[1], piece_type):
                    if verbose:
                        self.visualize_board()
                    continue

                self.died_pieces = self.remove_died_pieces(3 - piece_type)  # Remove the dead pieces of opponent
            else:
                self.previous_board = deepcopy(self.board)

            if verbose:
                self.visualize_board()  # Visualize the board again
                print()

            self.n_move += 1
            self.X_move = not self.X_move  # Players take turn


def judge(n_move, verbose=False):
    """
    返回谁赢、或者平局
    :param n_move: 第几手
    :param verbose: 是不是跟人下
    :return: 谁赢、或者平局
    """
    N = 5

    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.verbose = verbose
    go.set_board(piece_type, previous_board, board)
    go.n_move = n_move

    try:
        # 最近一手棋要下的位置
        action, x, y = readOutput()
    except:
        print("output.txt not found or invalid format")
        sys.exit(3 - piece_type)
    # 如果是落子
    if action == "MOVE":
        if not go.place_chess(x, y, piece_type):
            # 下了一个不能下的地方，胜利直接让给对面
            print('Game end.')
            print('The winner is {}'.format('X' if 3 - piece_type == 1 else 'O'))
            sys.exit(3 - piece_type)
        # 落子了，看看能不能提子
        go.died_pieces = go.remove_died_pieces(3 - piece_type)

    if verbose:
        go.visualize_board()
        print()
    # 如果游戏结束
    if go.game_end(piece_type, action):
        result = go.judge_winner()
        if verbose:
            print('Game end.')
            if result == 0:
                print('The game is a tie.')
            else:
                print('The winner is {}'.format('X' if result == 1 else 'O'))
        sys.exit(result)
    # 游戏没有结束，轮到对面下（这个文件是host，对手指上一手棋的对手）
    piece_type = 2 if piece_type == 1 else 1
    # 如果上一手是PASS,那棋盘没变
    if action == "PASS":
        go.previous_board = go.board
    # 对面下，当前方下之前的棋盘，下之后的棋盘
    writeNextInput(piece_type, go.previous_board, go.board)

    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--move", "-m", type=int, help="number of total moves", default=0)
    parser.add_argument("--verbose", "-v", type=bool, help="print board", default=False)
    args = parser.parse_args()

    judge(args.move, args.verbose)
