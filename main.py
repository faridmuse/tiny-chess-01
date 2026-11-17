"""Dev version of the tiny-chess-01 engine (readable; golfed into main.py later)."""
import os, json, urllib.request

VAL = (0, 100, 320, 330, 500, 900, 20000)
KN = (33, 31, 18, 14, -14, -18, -31, -33)
KI = (16, -16, 1, -1, 15, 17, -15, -17)
DIAG = (15, 17, -15, -17)
ORTH = (16, -16, 1, -1)
MATE = 100000
INF = 1000000
BUDGET = 15000  # nodes per move (tuned after benchmarking)

# PSTs, a1-first (index 0 = a1, 63 = h8). Classic simplified-eval values.
PAWN = (
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, -20, -20, 10, 10, 5,
    5, -5, -10, 0, 0, -10, -5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, 5, 10, 25, 25, 10, 5, 5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
    0, 0, 0, 0, 0, 0, 0, 0,
)
KNIGHT = (
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
)
BISHOP = (
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
)
ROOK = (
    0, 0, 0, 0, 0, 0, 0, 0,
    5, 10, 10, 10, 10, 10, 10, 5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    0, 0, 0, 5, 5, 0, 0, 0,
)
QUEEN = (
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -5, 0, 5, 5, 5, 5, 0, -5,
    0, 0, 5, 5, 5, 5, 0, -5,
    -10, 5, 5, 5, 5, 5, 0, -10,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20,
)
KING = (
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20,
)
KING_END = (
    -50, -30, -30, -30, -30, -30, -30, -50,
    -30, -30, 0, 0, 0, 0, -30, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -20, -10, 0, 0, -10, -20, -30,
    -50, -40, -30, -20, -20, -30, -40, -50,
)
PST = (None, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING)

B = [0] * 128
turn = 1
cast = 0
ep = -1
nodes = 0
T = {}
KIL = [[0, 0] for _ in range(64)]


def enc(f, t, pr=0):
    return f | (t << 7) | (pr << 14)


def attacked(sq, by):
    if by > 0:
        for o in (-15, -17):
            t = sq + o
            if not (t & 0x88) and B[t] == 1:
                return True
    else:
        for o in (15, 17):
            t = sq + o
            if not (t & 0x88) and B[t] == -1:
                return True
    for o in KN:
        t = sq + o
        if not (t & 0x88) and B[t] == by * 2:
            return True
    for o in KI:
        t = sq + o
        if not (t & 0x88) and B[t] == by * 6:
            return True
    for o in DIAG:
        t = sq + o
        while not (t & 0x88):
            p = B[t]
            if p:
                if p == by * 3 or p == by * 5:
                    return True
                break
            t += o
    for o in ORTH:
        t = sq + o
        while not (t & 0x88):
            p = B[t]
            if p:
                if p == by * 4 or p == by * 5:
                    return True
                break
            t += o
    return False


def king_sq(s):
    k = 6 * s
    for i in range(128):
        if not (i & 0x88) and B[i] == k:
            return i
    return -1


def gen_moves(captures_only=False):
    ms = []
    for sq in range(128):
        if sq & 0x88:
            continue
        p = B[sq]
        if p == 0 or (p > 0) != (turn > 0):
            continue
        a = abs(p)
        if a == 1:
            d = 16 * turn
            last = 7 if turn > 0 else 0
            t = sq + d
            if not (t & 0x88) and B[t] == 0:
                if (t >> 4) == last:
                    for pr in (5, 4, 3, 2):
                        ms.append(enc(sq, t, pr))
                elif not captures_only:
                    ms.append(enc(sq, t, 0))
                    if (sq >> 4) == (1 if turn > 0 else 6):
                        t2 = sq + 2 * d
                        if B[t2] == 0:
                            ms.append(enc(sq, t2, 0))
            for dd in (d - 1, d + 1):
                t = sq + dd
                if t & 0x88:
                    continue
                if (B[t] != 0 and (B[t] > 0) != (turn > 0)) or t == ep:
                    if (t >> 4) == last:
                        for pr in (5, 4, 3, 2):
                            ms.append(enc(sq, t, pr))
                    else:
                        ms.append(enc(sq, t, 0))
        elif a == 2 or a == 6:
            for o in (KN if a == 2 else KI):
                t = sq + o
                if t & 0x88:
                    continue
                if B[t] == 0 or (B[t] > 0) != (turn > 0):
                    if not captures_only or B[t] != 0:
                        ms.append(enc(sq, t, 0))
        else:
            dirs = DIAG if a == 3 else ORTH if a == 4 else KI
            for o in dirs:
                t = sq + o
                while not (t & 0x88):
                    if B[t] == 0:
                        if not captures_only:
                            ms.append(enc(sq, t, 0))
                    else:
                        if (B[t] > 0) != (turn > 0):
                            ms.append(enc(sq, t, 0))
                        break
                    t += o
    if not captures_only:
        if turn > 0:
            if cast & 1 and B[5] == 0 and B[6] == 0 and B[7] == 4 \
                    and not attacked(4, -1) and not attacked(5, -1) and not attacked(6, -1):
                ms.append(enc(4, 6))
            if cast & 2 and B[3] == 0 and B[2] == 0 and B[1] == 0 and B[0] == 4 \
                    and not attacked(4, -1) and not attacked(3, -1) and not attacked(2, -1):
                ms.append(enc(4, 2))
        else:
            if cast & 4 and B[117] == 0 and B[118] == 0 and B[119] == -4 \
                    and not attacked(116, 1) and not attacked(117, 1) and not attacked(118, 1):
                ms.append(enc(116, 118))
            if cast & 8 and B[115] == 0 and B[114] == 0 and B[113] == 0 and B[112] == -4 \
                    and not attacked(116, 1) and not attacked(115, 1) and not attacked(114, 1):
                ms.append(enc(116, 114))
    return ms


def do(m):
    global turn, cast, ep
    f = m & 127
    t = (m >> 7) & 127
    pr = m >> 14
    piece = B[f]
    cap_sq = t
    cap = B[t]
    if abs(piece) == 1 and t == ep and cap == 0:
        cap_sq = t - 16 * turn
        cap = B[cap_sq]
        B[cap_sq] = 0
    u = (f, t, cap_sq, cap, cast, ep, piece, pr)
    if abs(piece) == 6 and abs(t - f) == 2:
        if t > f:
            B[t - 1] = B[t + 1]
            B[t + 1] = 0
        else:
            B[t + 1] = B[t - 2]
            B[t - 2] = 0
    B[t] = pr * turn if pr else piece
    B[f] = 0
    if abs(piece) == 6:
        cast &= ~(3 if turn > 0 else 12)
    if f == 0 or t == 0:
        cast &= ~2
    if f == 7 or t == 7:
        cast &= ~1
    if f == 112 or t == 112:
        cast &= ~8
    if f == 119 or t == 119:
        cast &= ~4
    ep = f + 16 * turn if abs(piece) == 1 and abs(t - f) == 32 else -1
    turn = -turn
    return u


def undo(m, u):
    global turn, cast, ep
    f, t, cap_sq, cap, cast0, ep0, piece, pr = u
    turn = -turn
    cast = cast0
    ep = ep0
    if abs(piece) == 6 and abs(t - f) == 2:
        if t > f:
            B[t + 1] = B[t - 1]
            B[t - 1] = 0
        else:
            B[t - 2] = B[t + 1]
            B[t + 1] = 0
    B[f] = piece
    B[t] = 0
    if cap:
        B[cap_sq] = cap


def legal_moves(captures_only=False):
    out = []
    for m in gen_moves(captures_only):
        u = do(m)
        if not attacked(king_sq(-turn), turn):
            out.append(m)
        undo(m, u)
    return out


def evaluate():
    s = 0
    queens = 0
    for sq in range(128):
        if sq & 0x88:
            continue
        p = B[sq]
        if p:
            if abs(p) == 5:
                queens += 1
            i = (sq & 7) + ((sq >> 4) << 3)
            if p > 0:
                s += VAL[p] + PST[p][i]
            else:
                s -= VAL[-p] + PST[-p][63 - i]
    if queens == 0:
        # endgame: centralise the kings (re-score both kings with KING_END)
        for sq in range(128):
            if sq & 0x88:
                continue
            p = B[sq]
            if abs(p) == 6:
                i = (sq & 7) + ((sq >> 4) << 3)
                if p > 0:
                    s += KING_END[i] - KING[i]
                else:
                    s -= KING_END[63 - i] - KING[63 - i]
    return s


def order(moves, tt_move=0, ply=0):
    def key(m):
        if m == tt_move:
            return 1 << 30
        t = (m >> 7) & 127
        v = B[t]
        if v:
            return 10 * VAL[abs(v)] - VAL[abs(B[m & 127])] // 10
        if KIL[ply][0] == m or KIL[ply][1] == m:
            return 1000
        return 0
    moves.sort(key=key, reverse=True)
    return moves


class Abort(Exception):
    pass


def qsearch(alpha, beta, ply):
    global nodes
    nodes += 1
    if nodes > BUDGET:
        raise Abort
    if attacked(king_sq(turn), -turn):
        moves = order(legal_moves())
        if not moves:
            return -MATE + ply
        for m in moves:
            u = do(m)
            s = -qsearch(-beta, -alpha, ply + 1)
            undo(m, u)
            if s >= beta:
                return beta
            if s > alpha:
                alpha = s
        return alpha
    stand = evaluate() * turn
    if stand >= beta:
        return beta
    if stand > alpha:
        alpha = stand
    for m in order(legal_moves(True)):
        u = do(m)
        s = -qsearch(-beta, -alpha, ply + 1)
        undo(m, u)
        if s >= beta:
            return beta
        if s > alpha:
            alpha = s
    return alpha


def search(depth, alpha, beta, ply):
    global nodes
    nodes += 1
    if nodes > BUDGET:
        raise Abort
    if depth == 0:
        return qsearch(alpha, beta, ply)
    key = None
    ent = None
    tt_move = 0
    if depth >= 2:
        key = (tuple(B), turn, cast, ep)
        ent = T.get(key)
    if ent:
        ed, es, ef, em = ent
        tt_move = em
        if ed >= depth:
            if ef == 0:
                return es
            if ef == 1 and es > alpha:
                alpha = es
            if ef == 2 and es < beta:
                beta = es
            if alpha >= beta:
                return es
    moves = order(legal_moves(), tt_move, ply)
    if not moves:
        if attacked(king_sq(turn), -turn):
            return -MATE + ply
        return 0
    best = -INF
    flag = 2
    best_m = 0
    for m in moves:
        u = do(m)
        s = -search(depth - 1, -beta, -alpha, ply + 1)
        undo(m, u)
        if s > best:
            best = s
            best_m = m
        if s > alpha:
            alpha = s
            flag = 0
        if alpha >= beta:
            flag = 1
            if B[(m >> 7) & 127] == 0 and KIL[ply][0] != m:
                KIL[ply][1] = KIL[ply][0]
                KIL[ply][0] = m
            break
    if key is not None and abs(best) < MATE - 1000:
        T[key] = (depth, best, flag, best_m)
        if len(T) > 300000:
            T.clear()
    return best


def think():
    global nodes, depth_reached
    nodes = 0
    depth_reached = 0
    moves = order(legal_moves())
    if len(moves) == 1:
        return moves[0]
    best = moves[0]
    try:
        for depth in range(1, 17):
            alpha = -INF
            cur_best = None
            cur_score = -INF
            for m in moves:
                u = do(m)
                s = -search(depth - 1, -INF, -alpha, 1)
                undo(m, u)
                if s > cur_score:
                    cur_score = s
                    cur_best = m
                if s > alpha:
                    alpha = s
            best = cur_best
            depth_reached = depth
            moves.remove(best)
            moves.insert(0, best)
    except Abort:
        pass
    return best


def set_fen(fen):
    global turn, cast, ep, B
    parts = fen.split()
    B = [0] * 128
    rows = parts[0].split('/')
    for r, row in enumerate(rows):
        f = 0
        for ch in row:
            if ch.isdigit():
                f += int(ch)
            else:
                v = 'PNBRQK'.index(ch.upper()) + 1
                B[(7 - r) * 16 + f] = v if ch.isupper() else -v
                f += 1
    turn = 1 if parts[1] == 'w' else -1
    cast = 0
    if parts[2] != '-':
        if 'K' in parts[2]:
            cast |= 1
        if 'Q' in parts[2]:
            cast |= 2
        if 'k' in parts[2]:
            cast |= 4
        if 'q' in parts[2]:
            cast |= 8
    ep = -1
    if len(parts) > 3 and parts[3] != '-':
        ep = (ord(parts[3][0]) - 97) + (int(parts[3][1]) - 1) * 16


def uci(m):
    f = m & 127
    t = (m >> 7) & 127
    pr = m >> 14
    s = chr(97 + (f & 7)) + str((f >> 4) + 1) + chr(97 + (t & 7)) + str((t >> 4) + 1)
    if pr:
        s += 'qrbn'[5 - pr]
    return s


def post(path, obj):
    req = urllib.request.Request(
        URL + path, data=json.dumps(obj).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def main():
    global URL
    URL = os.environ['MAKEFUN_ENV_URL'].rstrip('/')
    while True:
        st = post('/game', {})
        if st.get('status') == 'done':
            print(json.dumps(st))
            return
        while st.get('status') == 'your_move':
            set_fen(st['fen'])
            u = uci(think())
            if u not in st.get('legal_moves', []):
                u = st['legal_moves'][0]
            st = post('/move', {'game': st['game'], 'move': u})


if __name__ == '__main__':
    main()
