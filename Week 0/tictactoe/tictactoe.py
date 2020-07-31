"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """

    nonEmptyFields = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] != None:
                nonEmptyFields += 1

    # initial state or even number of filled in fields
    if nonEmptyFields == 0 or nonEmptyFields % 2 == 0:
        return X
    # odd number of filled in fields or end of game
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    result = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                result.append((i, j))

    # return any value if terminal board
    if len(result) == 0:
        return 0

    return(set(result))


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    currentPlayer = player(board)
    boardCopy = copy.deepcopy(board)

    # raise exception if move is not valid
    if action not in actions(board):
        raise ValueError("Invalid move")

    # if move is valid, reflect in copy of board
    i = action[0]
    j = action[1]
    boardCopy[i][j] = currentPlayer

    return boardCopy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winner = None

    # check rows
    for row in board:
        if len(set(row)) == 1 and set(row) != {None}:
            winner = row[0]

    # check columns
    a = board[0]
    b = board[1]
    c = board[2]

    d = zip(a,b,c)

    for item in d:
        if len(set(item)) == 1 and set(item) != {None}:
            winner = item[0]

    # check diagonals
    upDown = []
    downUp = []
    for i in range(3):
        for j in range(3):
            if i == j:
                upDown.append(board[i][j])
            if i + j == 2:
                downUp.append(board[i][j])
    if len(set(upDown)) == 1 and set(upDown) != {None}:
        winner = upDown[0]
    elif len(set(downUp)) == 1 and set(downUp) != {None}:
        winner = downUp[0]

    return winner

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # if any fields are still empty and the game has not been won, game is not over/still in progress
    for row in board:
        # if None in row and winner(board) == None
        if None in row and winner(board) == None:
            return False

    # if there is a winner already (and all cells are not necessarily filled in), game is over
    if winner(board) != None:
        return True

    # if all cells are filled in, game is over (even if there is no winner)
    else:
        noEmptyCells = True
        # check if there are any empty cells on board
        for row in board:
            if None in row:
                noEmptyCells = False
        return noEmptyCells


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

# helper functions for minimax
def maxValue(board, alpha, beta):
    #print("MaxValue called")
    if terminal(board) == True:
        return utility(board)

    v = float("-inf")

    for action in actions(board):
        v = max(v, minValue(result(board, action), alpha, beta))
        alpha = max(alpha, v)
        # drop other nodes on finding value
        if alpha >= beta:
            return alpha

    return v


def minValue(board, alpha, beta):
    #print("MinValue called")
    if terminal(board) == True:
        return utility(board)

    v = float("inf")

    for action in actions(board):
        v = min(v, maxValue(result(board, action), alpha, beta))
        beta = min(beta, v)
        if alpha >= beta:
            return beta
    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    #if board is terminal, return None
    if terminal(board) == True:
        return None

    currentPlayer = player(board)

    # minimax implementation using alpha-beta pruning
    if currentPlayer == X:
        bestAction = None
        v = float("-inf")

        for action in actions(board):
            score = minValue(result(board, action), alpha=float("-inf"), beta=float("inf"))
            if score > v:
                v = score
                bestAction = action

    elif currentPlayer == O:
        bestAction = None
        v = float("inf")

        for action in actions(board):
            score = maxValue(result(board, action), alpha=float("-inf"), beta=float("inf"))
            if score < v:
                v = score
                bestAction = action

    return bestAction
