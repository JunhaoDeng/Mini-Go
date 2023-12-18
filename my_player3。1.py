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
                          [3, 3], [2, 4], [3, 1], [4, 2], [2, 0],
                          [0, 0], [0, 1], [2, 3], [0, 3],
                          [0, 4], [1, 4], [2, 1], [3, 4], [4, 4],
                          [4, 3], [1, 0], [4, 1], [4, 0], [3, 0], [1, 2], [3, 2]]
        # self.move_order = [[1, 1], [3, 3], [3, 1], [1, 3], [2, 2], [0, 2], [4, 2], [2, 0], [2, 4],
        #                    [0, 1], [0, 3], [1,4], [3,4], [4,3], [4,1], [3,0], [1,0], [1,2],
        #                    [3,2], [2,1], [2,3], [0,0], [4,4], [0,4], [4,0]]
        # self.move_order = [
        #     [2, 2],  # 中心
        #     [0, 0], [4, 4], [0, 4], [4, 0],  # 角落
        #     [2, 0], [2, 4], [0, 2], [4, 2],  # 边缘
        #     [1, 1], [3, 3], [1, 3], [3, 1],  # 次级角落
        #     [1, 2], [3, 2], [2, 1], [2, 3],  # 接近中心
        #     [0, 1], [0, 3], [1, 0], [1, 4], [3, 0], [3, 4], [4, 1], [4, 3]  # 其他边缘
        # ]
        # self.move_order = [
        #     [2, 2],  # 中心
        #     [1, 1], [1, 3], [3, 1],
        #
        #     # 角落
        #     [0, 0], [4, 4], [0, 4], [4, 0],
        #
        #     # 边缘
        #     [0, 2], [2, 0], [2, 4], [4, 2],
        #     [0, 1], [0, 3], [4, 1], [4, 3], [1, 0], [3, 0], [1, 4], [3, 4],
        #
        #     # 接近中心的点
        #     [3, 3], [1, 2], [3, 2], [2, 1], [2, 3]
        # ]
    def calcuScore(self, go, curPlayer, stoneType, alpha, beta, depth, scoreArray: list, intendedMove):
        '''
        :param board:
        :param curPlayer:
        :param stoneType:
        :param alpha:
        :param beta:
        :param depth:
        :param scoreArray:
        :param intendedMove:
        :param newBoard:
        :return:
        '''
        opRes = self.minMaxABCut(go, 1 - curPlayer, 3 - stoneType, alpha, beta, depth + 1)

        curMove = [[str(intendedMove[0]), str(intendedMove[1])], opRes[1]]

        scoreArray.append(curMove)


    def minMaxABCut(self, go: GO, curPlayer, piece_type, alpha, beta, depth):
        '''
        :param go:
        :param piece_type:
        :param curPlayer:
        :param alpha:
        :param beta:
        :param depth:
        :return:
        '''
        canMove = False
        if depth > 3:
            if curPlayer == 0:
                preScore = go.score(1) - go.score(2)
                if piece_type == 1:
                    score = preScore - 2.5
                else:
                    score = preScore + 2.5
            else:
                preScore = go.score(2) - go.score(1)
                if piece_type == 1:
                    score = preScore + 2.5
                else:
                    score = preScore - 2.5
            res = [None, str(score)]
            return res
        scoreArray = []
        max1 = -math.inf
        min1 = math.inf
        tempMove, tempScore = "", ""
        for i in range(len(self.moveOrder)):
            intendedMove = self.moveOrder[i]
            if go.valid_place_check(intendedMove[0], intendedMove[1], piece_type):
                canMove = True
                if go.score(1) + go.score(2) < 4:
                    return [intendedMove, math.inf]
                newgo = deepcopy(go)
                newgo.previous_board = deepcopy(newgo.board)
                newgo.board[intendedMove[0]][intendedMove[1]] = piece_type
                eatNum = len(newgo.remove_died_pieces(3 - piece_type))
                self.calcuScore(newgo, curPlayer, piece_type, alpha, beta, depth, scoreArray, intendedMove)
            else:
                continue
            endangeredScore = 2 * (self.numOfOneLibertyPieces(newgo.board, piece_type))
            if curPlayer == 0:
                for j in range(len(scoreArray)):
                    curScore = float(scoreArray[j][1]) + 3 * eatNum - endangeredScore + newgo.score(
                        piece_type) - newgo.score(
                        3 - piece_type)
                    if max1 < curScore:
                        max1 = curScore
                        tempScore = str(max1)
                        tempMove = scoreArray[j][0]
                        if beta <= max1:
                            tempRes = [tempMove, tempScore]
                            return tempRes
                        if alpha < max1:
                            alpha = max1
            elif curPlayer == 1:
                for j in range(len(scoreArray)):
                    curScore = float(scoreArray[j][1]) - 3 * eatNum + endangeredScore - (
                            newgo.score(piece_type) - newgo.score(3 - piece_type))
                    if min1 > curScore:
                        min1 = curScore
                        tempScore = str(min1)
                        tempMove = scoreArray[j][0]
                        if alpha >= min1:
                            tempRes = [tempMove, tempScore]

                            return tempRes
                        if beta > min1:
                            beta = min1
        if not canMove:
            if curPlayer == 0:
                preScore = go.score(1) - go.score(2)
                if piece_type == 1:
                    score = preScore - 2.5
                else:
                    score = preScore + 2.5
            else:
                preScore = go.score(2) - go.score(1)
                if piece_type == 1:
                    score = preScore + 2.5
                else:
                    score = preScore - 2.5
            return ["PASS", str(score)]
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
                        if piece not in visitedList:
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
