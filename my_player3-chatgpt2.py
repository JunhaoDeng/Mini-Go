import math
from collections import defaultdict
from read import readInput
from write import writeOutput
from host import GO
from copy import deepcopy


class MinMaxPlayer():
    def __init__(self):
        self.type = 'minMax'
        self.moveOrder = [[2, 2], [1, 1], [1, 3], [0, 2],
                          [3, 3], [2, 4], [3, 1], [4, 2],
                          [2, 0], [0, 0], [0, 1], [2, 3],
                          [0, 3], [0, 4], [1, 4], [2, 1],
                          [3, 4], [4, 4], [4, 3], [1, 0],
                          [4, 1], [4, 0], [3, 0], [1, 2], [3, 2]]

    def heuristic_evaluation(self, go: GO, piece_type):
        my_score = go.score(piece_type)
        opponent_score = go.score(3 - piece_type)
        endangered_pieces = self.numOfOneLibertyPieces(go.board, piece_type)
        opponent_endangered_pieces = self.numOfOneLibertyPieces(go.board, 3 - piece_type)
        return my_score - opponent_score + 2.5 * (opponent_endangered_pieces - endangered_pieces)

    def calcuScore(self, go, curPlayer, stoneType, alpha, beta, depth, scoreArray, intendedMove):
        opRes = self.minMaxABCut(go, 1 - curPlayer, 3 - stoneType, alpha, beta, depth + 1)
        curMove = [[str(intendedMove[0]), str(intendedMove[1])], opRes[1]]
        scoreArray.append(curMove)

    def minMaxABCut(self, go: GO, curPlayer, piece_type, alpha, beta, depth):
        if depth > 3:
            return [None, self.heuristic_evaluation(go, piece_type)]

        scoreArray = []
        tempMove, tempScore = "", ""

        for intendedMove in self.moveOrder:
            if go.valid_place_check(intendedMove[0], intendedMove[1], piece_type):
                newgo = deepcopy(go)
                newgo.previous_board = deepcopy(newgo.board)
                newgo.board[intendedMove[0]][intendedMove[1]] = piece_type
                eatNum = len(newgo.remove_died_pieces(3 - piece_type))
                self.calcuScore(newgo, curPlayer, piece_type, alpha, beta, depth, scoreArray, intendedMove)

                score_diff = go.score(piece_type) - go.score(3 - piece_type)
                if curPlayer == 0:
                    endangeredScore = 2 * (self.numOfOneLibertyPieces(go.board, piece_type))
                    max_score = -math.inf
                    for move_score in scoreArray:
                        temp_score = float(move_score[1]) + 3 * eatNum - endangeredScore + score_diff
                        if temp_score > max_score:
                            max_score = temp_score
                            tempScore = str(max_score)
                            tempMove = move_score[0]
                            if beta <= max_score:
                                return [tempMove, tempScore]
                            alpha = max(alpha, max_score)

        if not tempMove:
            return ["PASS", self.heuristic_evaluation(go, piece_type)]
        else:
            return [tempMove, tempScore]

    def numOfOneLibertyPieces(self, board, pieceType):
        visitedList = set()
        map = defaultdict(set)
        for i in range(5):
            for j in range(5):
                if board[i][j] == pieceType and str(i) + str(j) not in visitedList:
                    tmp = set()
                    liberty = self.countLiberty(board, i, j, pieceType, tmp)
                    for piece in tmp:
                        visitedList.add(piece)
                        map[liberty].add(piece)
        return len(map[1])

    def countLiberty(self, board, i, j, pieceType, visitedList: set):
        if i < 0 or j < 0 or i > 4 or j > 4 or board[i][j] == 3 - pieceType or str(i) + str(j) in visitedList:
            return 0
        if board[i][j] == 0:
            return 1
        visitedList.add(str(i) + str(j))
        return self.countLiberty(board, i - 1, j, pieceType, visitedList) + \
            self.countLiberty(board, i + 1, j, pieceType, visitedList) + \
            self.countLiberty(board, i, j - 1, pieceType, visitedList) + \
            self.countLiberty(board, i, j + 1, pieceType, visitedList)


if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MinMaxPlayer()
    action = player.minMaxABCut(go, 0, piece_type, -math.inf, math.inf, 0)
    writeOutput(action[0])
