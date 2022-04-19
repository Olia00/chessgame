#!/usr/bin/env pypy
# -*- coding: utf-8 -*-

import re, sys, time
from itertools import count
from collections import namedtuple
from turtle import screensize
import pygame
import pyautogui


###############################################################################
# Piece-Square tables. Tune these to change sunfish's behaviour
###############################################################################

piece = { 'P': 100, 'N': 280, 'B': 320, 'R': 479, 'Q': 929, 'K': 60000 }
pst = {
    'P': (   0,   0,   0,   0,   0,   0,   0,   0,
            78,  83,  86,  73, 102,  82,  119,  90,
             7,  29,  21,  44,  40,  31,  44,   7,
           -17,  16,  -2,  15,  14,   0,  15, -13,
           -26,   3,  10,   9,   6,   1,   0, -23,
           -22,   9,   5, -11, -10,  -2,   3, -19,
           -31,   8,  -7, -37, -36, -14,   3, -31,
             0,   0,   0,   0,   0,   0,   0,   0),
    'N': ( -66, -53, -75, -75, -10, -55, -58, -70,
            -3,  -6, 100, -36,   4,  62,  -4, -14,
            10,  67,   1,  74,  73,  27,  62,  -2,
            24,  24,  45,  37,  33,  41,  25,  17,
            -1,   5,  31,  21,  22,  35,   2,   0,
           -18,  10,  13,  22,  18,  15,  11, -14,
           -23, -15,   2,   0,   2,   0, -23, -20,
           -74, -23, -26, -24, -19, -35, -22, -69),
    'B': ( -59, -78, -82, -76, -23,-107, -37, -50,
           -11,  20,  35, -42, -39,  31,   2, -22,
            -9,  39, -32,  41,  52, -10,  28, -14,
            25,  17,  20,  34,  26,  25,  15,  10,
            13,  10,  17,  23,  17,  16,   0,   7,
            14,  25,  24,  15,   8,  25,  20,  15,
            19,  20,  11,   6,   7,   6,  20,  16,
            -7,   2, -15, -12, -14, -15, -10, -10),
    'R': (  35,  29,  33,   4,  37,  33,  56,  50,
            55,  29,  56,  67,  55,  62,  34,  60,
            19,  35,  28,  33,  45,  27,  25,  15,
             0,   5,  16,  13,  18,  -4,  -9,  -6,
           -28, -35, -16, -21, -13, -29, -46, -30,
           -42, -28, -42, -25, -25, -35, -26, -46,
           -53, -38, -31, -26, -29, -43, -44, -53,
           -30, -24, -18,   5,  -2, -18, -31, -32),
    'Q': (   6,   1,  -8,-104,  69,  24,  88,  26,
            14,  32,  60, -10,  20,  76,  57,  24,
            -2,  43,  32,  60,  72,  63,  43,   2,
             1, -16,  22,  17,  25,  20, -13,  -6,
           -14, -15,  -2,  -5,  -1, -10, -20, -22,
           -30,  -6, -13, -11, -16, -11, -16, -27,
           -36, -18,   0, -19, -15, -15, -21, -38,
           -39, -30, -31, -13, -31, -36, -34, -42),
    'K': (   4,  54,  47, -99, -99,  60,  83, -62,
           -32,  10,  55,  56,  56,  55,  10,   3,
           -62,  12, -57,  44, -67,  28,  37, -31,
           -55,  50,  11,  -4, -19,  13,   0, -49,
           -55, -43, -52, -28, -51, -47,  -8, -50,
           -47, -42, -43, -79, -64, -32, -29, -32,
            -4,   3, -14, -50, -57, -18,  13,   4,
            17,  30,  -3, -14,   6,  -1,  40,  18),
}
# Pad tables and join piece and pst dictionaries
for k, table in pst.items():
    padrow = lambda row: (0,) + tuple(x+piece[k] for x in row) + (0,)
    pst[k] = sum((padrow(table[i*8:i*8+8]) for i in range(8)), ())
    pst[k] = (0,)*20 + pst[k] + (0,)*20

###############################################################################
# Global constants
###############################################################################

# Our board is represented as a 120 character string. The padding allows for
# fast detection of moves that don't stay within the board.
A1, H1, A8, H8 = 91, 98, 21, 28
initial = (
    '         \n'  #   0 -  9
    '         \n'  #  10 - 19
    ' rnbqkbnr\n'  #  20 - 29
    ' pppppppp\n'  #  30 - 39
    ' ........\n'  #  40 - 49
    ' ........\n'  #  50 - 59
    ' ........\n'  #  60 - 69
    ' ........\n'  #  70 - 79
    ' PPPPPPPP\n'  #  80 - 89
    ' RNBQKBNR\n'  #  90 - 99
    '         \n'  # 100 -109
    '         \n'  # 110 -119
)

# Lists of possible moves for each piece type.
N, E, S, W = -10, 1, 10, -1
directions = {
    'P': (N, N+N, N+W, N+E),
    'N': (N+N+E, E+N+E, E+S+E, S+S+E, S+S+W, W+S+W, W+N+W, N+N+W),
    'B': (N+E, S+E, S+W, N+W),
    'R': (N, E, S, W),
    'Q': (N, E, S, W, N+E, S+E, S+W, N+W),
    'K': (N, E, S, W, N+E, S+E, S+W, N+W)
}

# Mate value must be greater than 8*queen + 2*(rook+knight+bishop)
# King value is set to twice this value such that if the opponent is
# 8 queens up, but we got the king, we still exceed MATE_VALUE.
# When a MATE is detected, we'll set the score to MATE_UPPER - plies to get there
# E.g. Mate in 3 will be MATE_UPPER - 6
MATE_LOWER = piece['K'] - 10*piece['Q']
MATE_UPPER = piece['K'] + 10*piece['Q']

# The table size is the maximum number of elements in the transposition table.
TABLE_SIZE = 1e7

# Constants for tuning search
QS_LIMIT = 219
EVAL_ROUGHNESS = 13
DRAW_TEST = True


###############################################################################
# Chess logic
###############################################################################

class Position(namedtuple('Position', 'board score wc bc ep kp')):
    """ A state of a chess game
    board -- a 120 char representation of the board
    score -- the board evaluation
    wc -- the castling rights, [west/queen side, east/king side]
    bc -- the opponent castling rights, [west/king side, east/queen side]
    ep - the en passant square
    kp - the king passant square
    """

    def gen_moves(self):
        # For each of our pieces, iterate through each possible 'ray' of moves,
        # as defined in the 'directions' map. The rays are broken e.g. by
        # captures or immediately in case of pieces such as knights.
        for i, p in enumerate(self.board):
            if not p.isupper(): continue
            for d in directions[p]:
                for j in count(i+d, d):
                    q = self.board[j]
                    # Stay inside the board, and off friendly pieces
                    if q.isspace() or q.isupper(): break
                    # Pawn move, double move and capture
                    if p == 'P' and d in (N, N+N) and q != '.': break
                    if p == 'P' and d == N+N and (i < A1+N or self.board[i+N] != '.'): break
                    if p == 'P' and d in (N+W, N+E) and q == '.' \
                            and j not in (self.ep, self.kp, self.kp-1, self.kp+1): break
                    # Move it
                    yield (i, j)
                    # Stop crawlers from sliding, and sliding after captures
                    if p in 'PNK' or q.islower(): break
                    # Castling, by sliding the rook next to the king
                    if i == A1 and self.board[j+E] == 'K' and self.wc[0]: yield (j+E, j+W)
                    if i == H1 and self.board[j+W] == 'K' and self.wc[1]: yield (j+W, j+E)

    def rotate(self):
        ''' Rotates the board, preserving enpassant '''
        return Position(
            self.board[::-1].swapcase(), -self.score, self.bc, self.wc,
            119-self.ep if self.ep else 0,
            119-self.kp if self.kp else 0)

    def nullmove(self):
        ''' Like rotate, but clears ep and kp '''
        return Position(
            self.board[::-1].swapcase(), -self.score,
            self.bc, self.wc, 0, 0)

    def move(self, move):
        i, j = move
        p, q = self.board[i], self.board[j]
        put = lambda board, i, p: board[:i] + p + board[i+1:]
        # Copy variables and reset ep and kp
        board = self.board
        wc, bc, ep, kp = self.wc, self.bc, 0, 0
        score = self.score + self.value(move)
        # Actual move
        board = put(board, j, board[i])
        board = put(board, i, '.')
        # Castling rights, we move the rook or capture the opponent's
        if i == A1: wc = (False, wc[1])
        if i == H1: wc = (wc[0], False)
        if j == A8: bc = (bc[0], False)
        if j == H8: bc = (False, bc[1])
        # Castling
        if p == 'K':
            wc = (False, False)
            if abs(j-i) == 2:
                kp = (i+j)//2
                board = put(board, A1 if j < i else H1, '.')
                board = put(board, kp, 'R')
        # Pawn promotion, double move and en passant capture
        if p == 'P':
            if A8 <= j <= H8:
                board = put(board, j, 'Q')
            if j - i == 2*N:
                ep = i + N
            if j == self.ep:
                board = put(board, j+S, '.')
        # We rotate the returned position, so it's ready for the next player
        return Position(board, score, wc, bc, ep, kp).rotate()

    def value(self, move):
        i, j = move
        p, q = self.board[i], self.board[j]
        # Actual move
        score = pst[p][j] - pst[p][i]
        # Capture
        if q.islower():
            score += pst[q.upper()][119-j]
        # Castling check detection
        if abs(j-self.kp) < 2:
            score += pst['K'][119-j]
        # Castling
        if p == 'K' and abs(i-j) == 2:
            score += pst['R'][(i+j)//2]
            score -= pst['R'][A1 if j < i else H1]
        # Special pawn stuff
        if p == 'P':
            if A8 <= j <= H8:
                score += pst['Q'][j] - pst['P'][j]
            if j == self.ep:
                score += pst['P'][119-(j+S)]
        return score

###############################################################################
# Search logic
###############################################################################

# lower <= s(pos) <= upper
Entry = namedtuple('Entry', 'lower upper')

class Searcher:
    def __init__(self):
        self.tp_score = {}
        self.tp_move = {}
        self.history = set()
        self.nodes = 0

    def bound(self, pos, gamma, depth, root=True):
        """ returns r where
                s(pos) <= r < gamma    if gamma > s(pos)
                gamma <= r <= s(pos)   if gamma <= s(pos)"""
        self.nodes += 1

        # Depth <= 0 is QSearch. Here any position is searched as deeply as is needed for
        # calmness, and from this point on there is no difference in behaviour depending on
        # depth, so so there is no reason to keep different depths in the transposition table.
        depth = max(depth, 0)

        # Sunfish is a king-capture engine, so we should always check if we
        # still have a king. Notice since this is the only termination check,
        # the remaining code has to be comfortable with being mated, stalemated
        # or able to capture the opponent king.
        if pos.score <= -MATE_LOWER:
            return -MATE_UPPER

        # We detect 3-fold captures by comparing against previously
        # _actually played_ positions.
        # Note that we need to do this before we look in the table, as the
        # position may have been previously reached with a different score.
        # This is what prevents a search instability.
        # FIXME: This is not true, since other positions will be affected by
        # the new values for all the drawn positions.
        if DRAW_TEST:
            if not root and pos in self.history:
                return 0

        # Look in the table if we have already searched this position before.
        # We also need to be sure, that the stored search was over the same
        # nodes as the current search.
        entry = self.tp_score.get((pos, depth, root), Entry(-MATE_UPPER, MATE_UPPER))
        if entry.lower >= gamma and (not root or self.tp_move.get(pos) is not None):
            return entry.lower
        if entry.upper < gamma:
            return entry.upper

        # Here extensions may be added
        # Such as 'if in_check: depth += 1'

        # Generator of moves to search in order.
        # This allows us to define the moves, but only calculate them if needed.
        def moves():
            # First try not moving at all. We only do this if there is at least one major
            # piece left on the board, since otherwise zugzwangs are too dangerous.
            if depth > 0 and not root and any(c in pos.board for c in 'RBNQ'):
                yield None, -self.bound(pos.nullmove(), 1-gamma, depth-3, root=False)
            # For QSearch we have a different kind of null-move, namely we can just stop
            # and not capture anything else.
            if depth == 0:
                yield None, pos.score
            # Then killer move. We search it twice, but the tp will fix things for us.
            # Note, we don't have to check for legality, since we've already done it
            # before. Also note that in QS the killer must be a capture, otherwise we
            # will be non deterministic.
            killer = self.tp_move.get(pos)
            if killer and (depth > 0 or pos.value(killer) >= QS_LIMIT):
                yield killer, -self.bound(pos.move(killer), 1-gamma, depth-1, root=False)
            # Then all the other moves
            for move in sorted(pos.gen_moves(), key=pos.value, reverse=True):
            #for val, move in sorted(((pos.value(move), move) for move in pos.gen_moves()), reverse=True):
                # If depth == 0 we only try moves with high intrinsic score (captures and
                # promotions). Otherwise we do all moves.
                if depth > 0 or pos.value(move) >= QS_LIMIT:
                    yield move, -self.bound(pos.move(move), 1-gamma, depth-1, root=False)

        # Run through the moves, shortcutting when possible
        best = -MATE_UPPER
        for move, score in moves():
            best = max(best, score)
            if best >= gamma:
                # Clear before setting, so we always have a value
                if len(self.tp_move) > TABLE_SIZE: self.tp_move.clear()
                # Save the move for pv construction and killer heuristic
                self.tp_move[pos] = move
                break

        # Stalemate checking is a bit tricky: Say we failed low, because
        # we can't (legally) move and so the (real) score is -infty.
        # At the next depth we are allowed to just return r, -infty <= r < gamma,
        # which is normally fine.
        # However, what if gamma = -10 and we don't have any legal moves?
        # Then the score is actaully a draw and we should fail high!
        # Thus, if best < gamma and best < 0 we need to double check what we are doing.
        # This doesn't prevent sunfish from making a move that results in stalemate,
        # but only if depth == 1, so that's probably fair enough.
        # (Btw, at depth 1 we can also mate without realizing.)
        if best < gamma and best < 0 and depth > 0:
            is_dead = lambda pos: any(pos.value(m) >= MATE_LOWER for m in pos.gen_moves())
            if all(is_dead(pos.move(m)) for m in pos.gen_moves()):
                in_check = is_dead(pos.nullmove())
                best = -MATE_UPPER if in_check else 0

        # Clear before setting, so we always have a value
        if len(self.tp_score) > TABLE_SIZE: self.tp_score.clear()
        # Table part 2
        if best >= gamma:
            self.tp_score[pos, depth, root] = Entry(best, entry.upper)
        if best < gamma:
            self.tp_score[pos, depth, root] = Entry(entry.lower, best)

        return best

    def search(self, pos, history=()):
        """ Iterative deepening MTD-bi search """
        self.nodes = 0
        if DRAW_TEST:
            self.history = set(history)
            # print('# Clearing table due to new history')
            self.tp_score.clear()

        # In finished games, we could potentially go far enough to cause a recursion
        # limit exception. Hence we bound the ply.
        for depth in range(1, 1000):
            # The inner loop is a binary search on the score of the position.
            # Inv: lower <= score <= upper
            # 'while lower != upper' would work, but play tests show a margin of 20 plays
            # better.
            lower, upper = -MATE_UPPER, MATE_UPPER
            while lower < upper - EVAL_ROUGHNESS:
                gamma = (lower+upper+1)//2
                score = self.bound(pos, gamma, depth)
                if score >= gamma:
                    lower = score
                if score < gamma:
                    upper = score
            # We want to make sure the move to play hasn't been kicked out of the table,
            # So we make another call that must always fail high and thus produce a move.
            self.bound(pos, lower, depth)
            # If the game hasn't finished we can retrieve our move from the
            # transposition table.
            yield depth, self.tp_move.get(pos), self.tp_score.get((pos, depth, True)).lower

###############################################################################
# User interface
###############################################################################

# Python 2 compatability
if sys.version_info[0] == 2:
    input = raw_input


def parse(c):
    fil, rank = ord(c[0]) - ord('a'), int(c[1]) - 1
    return A1 + fil - 10*rank


def render(i):
    rank, fil = divmod(i - A1, 10)
    return chr(fil + ord('a')) + str(-rank + 1)


def print_pos(pos):
    print()
    uni_pieces = {'R':'♜', 'N':'♞', 'B':'♝', 'Q':'♛', 'K':'♚', 'P':'♟',
                  'r':'♖', 'n':'♘', 'b':'♗', 'q':'♕', 'k':'♔', 'p':'♙', '.':'·'}
    for i, row in enumerate(pos.board.split()):
        print(' ', 8-i, ' '.join(uni_pieces.get(p, p) for p in row))
    print('    a b c d e f g h \n\n')

# def chane_scale(asset, height):
#     asset = pygame.transform.scale(asset, (50, 50))

width, height = pyautogui.size()
scale = (height/10-10, height/10-10)
white_king = pygame.image.load('Assets/Pieces/White_King.png')
white_king = pygame.transform.scale(white_king, scale)
black_king = pygame.image.load('Assets/Pieces/Black_King.png')
black_king = pygame.transform.scale(black_king, scale)

white_queen = pygame.image.load('Assets/Pieces/White_Queen.png')
white_queen = pygame.transform.scale(white_queen, scale)
black_queen = pygame.image.load('Assets/Pieces/Black_Queen.png')
black_queen = pygame.transform.scale(black_queen, scale)

white_rook = pygame.image.load('Assets/Pieces/White_Rook.png')
white_rook = pygame.transform.scale(white_rook, scale)
black_rook = pygame.image.load('Assets/Pieces/Black_Rook.png')
black_rook = pygame.transform.scale(black_rook, scale)

white_knight = pygame.image.load('Assets/Pieces/White_Knight.png')
white_knight = pygame.transform.scale(white_knight, scale)
black_knight = pygame.image.load('Assets/Pieces/Black_Knight.png')
black_knight = pygame.transform.scale(black_knight, scale)

white_bishop = pygame.image.load('Assets/Pieces/White_Bishop.png')
white_bishop = pygame.transform.scale(white_bishop, scale)
black_bishop = pygame.image.load('Assets/Pieces/Black_Bishop.png')
black_bishop = pygame.transform.scale(black_bishop, scale)

white_pawn = pygame.image.load('Assets/Pieces/White_Pawn.png')
white_pawn = pygame.transform.scale(white_pawn, scale)
black_pawn = pygame.image.load('Assets/Pieces/Black_Pawn.png')
black_pawn = pygame.transform.scale(black_pawn, scale)

white_field = pygame.image.load('Assets/Board/White_Pole.png')
white_field = pygame.transform.scale(white_field, scale)
black_field = pygame.image.load('Assets/Board/Black_Pole.png')
black_field = pygame.transform.scale(black_field, scale)

selected_field = pygame.image.load('Assets/Board/Selected_Pole.png')
selected_field = pygame.transform.scale(selected_field, scale)

empty_field = pygame.image.load('Assets/Board/Empty_Pole.png')
empty_field = pygame.transform.scale(empty_field, scale)

frame_field = pygame.image.load('Assets/Board/Board_Pole.png')
frame_field = pygame.transform.scale(frame_field, scale)

field_1 = pygame.image.load('Assets/Board/1.png')
field_1 = pygame.transform.scale(field_1, scale)

field_2 = pygame.image.load('Assets/Board/2.png')
field_2 = pygame.transform.scale(field_2, scale)

field_3 = pygame.image.load('Assets/Board/3.png')
field_3 = pygame.transform.scale(field_3, scale)

field_4 = pygame.image.load('Assets/Board/4.png')
field_4 = pygame.transform.scale(field_4, scale)

field_5 = pygame.image.load('Assets/Board/5.png')
field_5 = pygame.transform.scale(field_5, scale)

field_6 = pygame.image.load('Assets/Board/6.png')
field_6 = pygame.transform.scale(field_6, scale)

field_7 = pygame.image.load('Assets/Board/7.png')
field_7 = pygame.transform.scale(field_7, scale)

field_8 = pygame.image.load('Assets/Board/8.png')
field_8 = pygame.transform.scale(field_8, scale)

field_A = pygame.image.load('Assets/Board/A.png')
field_A = pygame.transform.scale(field_A, scale)

field_B = pygame.image.load('Assets/Board/B.png')
field_B = pygame.transform.scale(field_B, scale)

field_C = pygame.image.load('Assets/Board/C.png')
field_C = pygame.transform.scale(field_C, scale)

field_D = pygame.image.load('Assets/Board/D.png')
field_D = pygame.transform.scale(field_D, scale)

field_E = pygame.image.load('Assets/Board/E.png')
field_E = pygame.transform.scale(field_E, scale)

field_F = pygame.image.load('Assets/Board/F.png')
field_F = pygame.transform.scale(field_F, scale)

field_G = pygame.image.load('Assets/Board/G.png')
field_G = pygame.transform.scale(field_G, scale)

field_H = pygame.image.load('Assets/Board/H.png')
field_H = pygame.transform.scale(field_H, scale)

# assets = [ white_king, black_king, white_queen, black_queen, white_rook, black_rook, \
#         white_knight, black_knight, white_bishop, black_bishop, white_pawn, black_pawn, \
#         white_field, black_field, selected_field, empty_field, frame_field, field_1, field_2, \
#         field_3, field_4, field_5, field_6, field_7, field_8, field_A, field_B, field_C, \
#         field_D, field_E, field_F, field_G, field_H
#         ]

# print(width, height/10)
# for file in assets:
#     file = pygame.transform.scale(file, (height/10, height/10))
#     chane_scale(file, height)
# field = []
# for file in os.listdir('Assets/Board'):
#     # if file.endswith('.png'):
#     field[file] = pygame.image.load('Assets/Board/{}'.format(os.path.basename(file)))
BACK = (0, 0, 0)
WIDTH, HEIGHT = 10 * empty_field.get_width(), 10 * empty_field.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blindfold Chess")
FPS = 60

def draw_board():     
    WIN.fill(BACK)
    board = ['FP',  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'FP', 
             '8',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '8',
             '7',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '7',
             '6',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '6',
             '5',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '5',
             '4',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '4',
             '3',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '3',
             '2',   'b', 'w', 'b', 'w', 'b', 'w', 'b', 'w', '2',
             '1',   'w', 'b', 'w', 'b', 'w', 'b', 'w', 'b', '1',
             'FP',  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'FP'
            ]

    pos_x = 0
    pos_y = 0
    row = 1
    for i in board:
        if i == 'FP': pole = frame_field
        if i == 'A': pole = field_A
        if i == 'B': pole = field_B
        if i == 'C': pole = field_C
        if i == 'D': pole = field_D
        if i == 'E': pole = field_E
        if i == 'F': pole = field_F
        if i == 'G': pole = field_G
        if i == 'H': pole = field_H
        if i == '1': pole = field_1
        if i == '2': pole = field_2
        if i == '3': pole = field_3
        if i == '4': pole = field_4
        if i == '5': pole = field_5
        if i == '6': pole = field_6
        if i == '7': pole = field_7
        if i == '8': pole = field_8
        if i == 'b': pole = black_field
        if i == 'w': pole = white_field
        WIN.blit(pole, (pos_x, pos_y))
        pos_x += empty_field.get_height()
        if row%10 == 0:
            pos_y += empty_field.get_height()
            pos_x = 0
        row += 1

def draw_pieces(pos):    
    draw_board()
    uni_pieces = {'R':white_rook, 'N':white_knight, 'B':white_bishop, 'Q':white_queen, 'K':white_king, 'P':white_pawn,
                  'r':black_rook, 'n':black_knight, 'b':black_bishop, 'q':black_queen, 'k':black_king, 'p':black_pawn, '.':empty_field}
    pos_x = empty_field.get_height()
    pos_y =empty_field.get_height()
    for i, row in enumerate(pos.board.split()):
        for p in row:
            piece = uni_pieces.get(p, p)
            piece.get_rect(center=(empty_field.get_width()/2, empty_field.get_height()/2))
            WIN.blit(piece, (pos_x, pos_y))
            pos_x += empty_field.get_height()
        pos_x = empty_field.get_height()
        pos_y += empty_field.get_height()

def main():
    pygame.init()
    clock = pygame.time.Clock()
    run = True
    hist = [Position(initial, 0, (True,True), (True,True), 0, 0)]
    searcher = Searcher()

    while run:
        # pygame.event.get()
        # pygame.event.pump()
        # pygame.event.wait()
        # pygame.event.poll()
        clock.tick(FPS)
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                exit()

        while True:
            # print_pos(hist[-1])
            draw_pieces(hist[-1])            
            pygame.display.update()
            pygame.event.poll()
            if hist[-1].score <= -MATE_LOWER:
                print("You lost")
                break
            
            # We query the user until she enters a (pseudo) legal move.
            move = None

            
            while move not in hist[-1].gen_moves():                
                match = re.match('([a-h][1-8])'*2, input('Your move: '))
                # print(match)
                if match:
                    move = parse(match.group(1)), parse(match.group(2))
                
                else:
                    #Inform the user when invalid input (e.g. "help") is entered
                    print("Please enter a move like g8f6")
            hist.append(hist[-1].move(move))

            # After our move we rotate the board and print it again.
            # This allows us to see the effect of our move.
            pygame.event.poll()
            # print_pos(hist[-1].rotate())
            draw_pieces(hist[-1].rotate())            
            pygame.display.update()

            if hist[-1].score <= -MATE_LOWER:
                print("You won")
                break

            # Fire up the engine to look for a move.
            start = time.time()
            for _depth, move, score in searcher.search(hist[-1], hist):
                if time.time() - start > 1:
                    break

            if score == MATE_UPPER:
                print("Checkmate!")

            # The black player moves from a rotated position, so we have to
            # 'back rotate' the move before printing it.
            
            print("My move:", render(119-move[0]) + render(119-move[1]))
            hist.append(hist[-1].move(move))
    pygame.quit()
    

if __name__ == '__main__':
    main()
