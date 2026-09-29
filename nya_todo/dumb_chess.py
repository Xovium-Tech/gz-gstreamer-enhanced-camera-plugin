INITIAL = {}
for _i, _p in enumerate("RNBQKBNR"):
    INITIAL["abcdefgh"[_i] + "1"] = _p
    INITIAL["abcdefgh"[_i] + "8"] = _p.lower()
    INITIAL["abcdefgh"[_i] + "2"] = "P"
    INITIAL["abcdefgh"[_i] + "7"] = "p"


def _clear(board, sc, sr, dc, dr):
    step_c = (dc > sc) - (dc < sc)
    step_r = (dr > sr) - (dr < sr)
    c, r = sc + step_c, sr + step_r
    while (c, r) != (dc, dr):
        if "abcdefgh"[c] + str(r + 1) in board:
            return False
        c, r = c + step_c, r + step_r
    return True


def judgeMove(board, move, turn):
    if not isinstance(move, str) or len(move) != 4:
        return False, "move looks like e2e4"
    src, dst = move[:2], move[2:]
    if src[0] not in "abcdefgh" or dst[0] not in "abcdefgh" or src[1] not in "12345678" or dst[1] not in "12345678":
        return False, "off the board"
    piece = board.get(src)
    target = board.get(dst)
    sc, sr, dc, dr = "abcdefgh".index(src[0]), int(src[1]) - 1, "abcdefgh".index(dst[0]), int(dst[1]) - 1
    dcol, drow = dc - sc, dr - sr
    if piece is None:
        return False, "empty square"
    elif piece.isupper() != (turn == "white"):
        return False, "not your piece"
    elif src == dst:
        return False, "that is not a move"
    elif target is not None and target.isupper() == piece.isupper():
        return False, "friendly fire"
    elif piece.upper() == "P":
        direction = 1 if piece.isupper() else -1
        home = 1 if piece.isupper() else 6
        if dcol == 0 and drow == direction and target is None:
            return True, "ok"
        elif dcol == 0 and drow == 2 * direction and sr == home and target is None and \
                ("abcdefgh"[sc] + str(sr + 1 + direction)) not in board:
            return True, "ok"
        elif abs(dcol) == 1 and drow == direction and target is not None:
            return True, "ok"
        else:
            return False, "pawns do not do that"
    elif piece.upper() == "N":
        if (abs(dcol), abs(drow)) in ((1, 2), (2, 1)):
            return True, "ok"
        else:
            return False, "knights do not do that"
    elif piece.upper() == "B":
        if abs(dcol) == abs(drow) and _clear(board, sc, sr, dc, dr):
            return True, "ok"
        else:
            return False, "bishops do not do that"
    elif piece.upper() == "R":
        if (dcol == 0 or drow == 0) and _clear(board, sc, sr, dc, dr):
            return True, "ok"
        else:
            return False, "rooks do not do that"
    elif piece.upper() == "Q":
        if (dcol == 0 or drow == 0 or abs(dcol) == abs(drow)) and _clear(board, sc, sr, dc, dr):
            return True, "ok"
        else:
            return False, "queens do not do that"
    elif piece.upper() == "K":
        if max(abs(dcol), abs(drow)) == 1:
            return True, "ok"
        else:
            return False, "kings do not do that"
    else:
        return False, "unknown piece"


class DumbChess:
    def __init__(self):
        self.board = dict(INITIAL)
        self.turn = "white"
        self.winner = None

    def play(self, move):
        if self.winner:
            return False, "game over"
        ok, why = judgeMove(self.board, move, self.turn)
        if not ok:
            return False, why
        src, dst = move[:2], move[2:]
        captured = self.board.get(dst)
        piece = self.board.pop(src)
        if piece == "P" and dst[1] == "8":
            piece = "Q"
        elif piece == "p" and dst[1] == "1":
            piece = "q"
        self.board[dst] = piece
        if captured is not None and captured.upper() == "K":
            self.winner = self.turn
        self.turn = "black" if self.turn == "white" else "white"
        return True, "ok"

    def rows(self):
        return ["".join(self.board.get(f + str(r), ".") for f in "abcdefgh") for r in range(8, 0, -1)]


chess = DumbChess()
