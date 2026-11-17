import json, os, sys, urllib.request
URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")

def post(p, b):
    r = urllib.request.Request(URL + p, data=json.dumps(b).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(r) as z:
        return json.load(z)

V = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}
PST = {
 "p": [0,0,0,0,0,0,0,0, 50,50,50,50,50,50,50,50, 10,10,20,30,30,20,10,10, 5,5,10,25,25,10,5,5, 0,0,0,20,20,0,0,0, 5,-5,-10,0,0,-10,-5,5, 5,10,10,-20,-20,10,10,5, 0,0,0,0,0,0,0,0],
 "n": [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
 "b": [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
 "r": [0,0,0,0,0,0,0,0, 5,10,10,10,10,10,10,5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, 0,0,0,5,5,0,0,0],
 "q": [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5, 0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
 "k": [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10, 20,20,0,0,0,0,20,20, 20,30,10,0,0,10,30,20],
}
KPST_E = [ -50,-40,-30,-20,-20,-30,-40,-50, -30,-20,-10,0,0,-10,-20,-30, -30,-10,20,30,30,20,-10,-30, -30,-10,30,40,40,30,-10,-30, -30,-10,30,40,40,30,-10,-30, -30,-10,20,30,30,20,-10,-30, -30,-30,0,0,0,0,-30,-30, -50,-30,-30,-30,-30,-30,-30,-50]

def parse(fen):
    f = fen.split()
    b = [""] * 64
    for i, row in enumerate(f[0].split("/")):
        c = 0
        for ch in row:
            if ch.isdigit(): c += int(ch)
            else: b[i * 8 + c] = ch; c += 1
    ep = -1
    if len(f) > 3 and f[3] != "-":
        ep = (ord(f[3][0]) - 97) + (8 - int(f[3][1])) * 8
    return b, f[1], f[2], ep

def sq_of(p): return chr(97 + p % 8) + str(8 - p // 8)

N, S, E, W = -8, 8, 1, -1
DIRS = {"n": [N+N+E, N+N+W, S+S+E, S+S+W, E+E+N, E+E+S, W+W+N, W+W+S], "b": [N+E, N+W, S+E, S+W],
        "r": [N, S, E, W], "q": [N, S, E, W, N+E, N+W, S+E, S+W], "k": [N, S, E, W, N+E, N+W, S+E, S+W]}

def attacked(b, s, by_white):
    for d in DIRS["n"]:
        t = s + d
        if 0 <= t < 64 and abs(t % 8 - s % 8) <= 2 and b[t] == ("N" if by_white else "n"): return True
    for d in DIRS["q"]:
        t = s
        while True:
            prev = t; t += d
            if not (0 <= t < 64) or abs(t % 8 - prev % 8) > 1: break
            p = b[t]
            if p:
                pl = p.lower()
                if p.isupper() == by_white:
                    if pl == "q" or (pl == "b" and d in DIRS["b"]) or (pl == "r" and d in DIRS["r"]): return True
                break
    for d in (7, 9) if by_white else (-9, -7):
        t = s + d
        if 0 <= t < 64 and abs(t % 8 - s % 8) == 1 and b[t] == ("P" if by_white else "p"): return True
    for d in DIRS["k"]:
        t = s + d
        if 0 <= t < 64 and abs(t % 8 - s % 8) <= 1 and b[t] == ("K" if by_white else "k"): return True
    return False

def moves(b, turn, cast, ep):
    white = turn == "w"
    out = []
    for s in range(64):
        p = b[s]
        if not p or p.isupper() != white: continue
        pl = p.lower()
        if pl == "p":
            fwd = -8 if white else 8
            t = s + fwd
            if 0 <= t < 64 and not b[t]:
                if t // 8 in (0, 7):
                    for pr in "qrbn": out.append((s, t, pr))
                else:
                    out.append((s, t, None))
                    if s // 8 == (6 if white else 1) and not b[s + 2 * fwd]: out.append((s, s + 2 * fwd, None))
            for dd in (-1, 1):
                t = s + fwd + dd
                if 0 <= t < 64 and abs(t % 8 - s % 8) == 1:
                    if b[t] and b[t].isupper() != white:
                        if t // 8 in (0, 7):
                            for pr in "qrbn": out.append((s, t, pr))
                        else: out.append((s, t, None))
                    elif t == ep and ep >= 0: out.append((s, t, None))
        elif pl in ("n", "k"):
            for d in DIRS[pl]:
                t = s + d
                if 0 <= t < 64 and abs(t % 8 - s % 8) <= 2 and (not b[t] or b[t].isupper() != white):
                    out.append((s, t, None))
            if pl == "k":
                if white and s == 60:
                    if "K" in cast and not b[61] and not b[62] and b[63] == "R" and not attacked(b, 60, False) and not attacked(b, 61, False) and not attacked(b, 62, False): out.append((60, 62, None))
                    if "Q" in cast and not b[59] and not b[58] and not b[57] and b[56] == "R" and not attacked(b, 60, False) and not attacked(b, 59, False) and not attacked(b, 58, False): out.append((60, 58, None))
                if (not white) and s == 4:
                    if "k" in cast and not b[5] and not b[6] and b[7] == "r" and not attacked(b, 4, True) and not attacked(b, 5, True) and not attacked(b, 6, True): out.append((4, 6, None))
                    if "q" in cast and not b[3] and not b[2] and not b[1] and b[0] == "r" and not attacked(b, 4, True) and not attacked(b, 3, True) and not attacked(b, 2, True): out.append((4, 2, None))
        else:
            for d in DIRS[pl]:
                t = s
                while True:
                    prev = t; t += d
                    if not (0 <= t < 64) or abs(t % 8 - prev % 8) > 1: break
                    if b[t]:
                        if b[t].isupper() != white: out.append((s, t, None))
                        break
                    out.append((s, t, None))
    return out

def apply(b, m, turn, cast, ep):
    s, t, pr = m
    cap = b[t]; pawn = b[s]; new_ep = -1
    b[t] = pawn; b[s] = ""
    if pawn in "Pp":
        if t == ep and ep >= 0 and not cap:
            cs = t + 8 if pawn == "P" else t - 8
            cap = b[cs]; b[cs] = ""
        if abs(t - s) == 16: new_ep = (s + t) // 2
    if pr: b[t] = pr.upper() if turn == "w" else pr
    if pawn == "K" and s == 60:
        if t == 62: b[63] = ""; b[61] = "R"
        if t == 58: b[56] = ""; b[59] = "R"
    if pawn == "k" and s == 4:
        if t == 6: b[7] = ""; b[5] = "r"
        if t == 2: b[0] = ""; b[3] = "r"
    c = cast
    for ch, cond in [("K", pawn == "K" or s == 63 or t == 63), ("Q", pawn == "K" or s == 56 or t == 56),
                     ("k", pawn == "k" or s == 7 or t == 7), ("q", pawn == "k" or s == 0 or t == 0)]:
        if cond and ch in c: c = c.replace(ch, "")
    return (s, t, cap, cast, ep, c, new_ep)

def unapply(b, m, u, turn):
    s, t, pr = m
    us, ut, cap, ucast, uep, nc, nep = u
    moved = b[t]
    if pr: moved = "P" if turn == "w" else "p"
    ep_cap = moved in "Pp" and t == uep and uep >= 0
    b[s] = moved
    if cap and not ep_cap: b[t] = cap
    else: b[t] = ""
    if ep_cap:
        b[t + 8 if moved == "P" else t - 8] = cap
    if moved == "K" and s == 60:
        if t == 62: b[61] = ""; b[63] = "R"
        if t == 58: b[59] = ""; b[56] = "R"
    if moved == "k" and s == 4:
        if t == 6: b[5] = ""; b[7] = "r"
        if t == 2: b[3] = ""; b[0] = "r"

def king_sq(b, white): return b.index("K" if white else "k")

NODES = [0]
BUDGET = 100000

def ev(b, white):
    sc = 0
    wm = bn = 0
    for i in range(64):
        p = b[i]
        if not p: continue
        pl = p.lower()
        if p == "K": wm += 1
        elif p == "k": bn += 1
        sc += (V[pl] + PST[pl][i]) if p.isupper() else -(V[pl] + PST[pl][i ^ 56])
    if wm + bn <= 6:
        for i in range(64):
            p = b[i]
            if p == "K": sc += KPST_E[i]
            elif p == "k": sc -= KPST_E[i ^ 56]
    return sc if white else -sc

def qsearch(b, turn, cast, ep, a, be):
    NODES[0] += 1
    white = turn == "w"
    stand = ev(b, white)
    if stand >= be: return be
    if stand > a: a = stand
    ms = [m for m in moves(b, turn, cast, ep) if b[m[1]] or m[2]]
    ms.sort(key=lambda m: -(V.get(b[m[1]].lower(), 0) * 10 - V.get((b[m[0]] or "p").lower(), 0)))
    for m in ms:
        u = apply(b, m, turn, cast, ep)
        if attacked(b, king_sq(b, white), not white):
            unapply(b, m, u, turn); continue
        v = -qsearch(b, "b" if turn == "w" else "w", u[5], u[6], -be, -a)
        unapply(b, m, u, turn)
        if v >= be: return be
        if v > a: a = v
    return a

KILL = [None] * 40

def search(b, turn, cast, ep, d, a, be, ply=0):
    white = turn == "w"
    if attacked(b, king_sq(b, white), not white): d += 1
    if d <= 0 or NODES[0] > BUDGET: return qsearch(b, turn, cast, ep, a, be)
    NODES[0] += 1
    best = -99999
    ms = moves(b, turn, cast, ep)
    ms.sort(key=lambda m: -(V.get(b[m[1]].lower(), 0) * 10 - V.get((b[m[0]] or "p").lower(), 0)) + (300 if m == KILL[ply] else 0))
    legal = 0
    for m in ms:
        u = apply(b, m, turn, cast, ep)
        if attacked(b, king_sq(b, white), not white):
            unapply(b, m, u, turn); continue
        legal += 1
        v = -search(b, "b" if turn == "w" else "w", u[5], u[6], d - 1, -be, -a, ply + 1)
        unapply(b, m, u, turn)
        if v > best: best = v; KILL[ply] = m
        if v > a: a = v
        if a >= be: break
    if legal == 0:
        return (-30000 + (10 - d)) if attacked(b, king_sq(b, white), not white) else 0
    return best

SEEN = []
def bkey(b, turn): return ("".join(b), turn)

def best_move(fen):
    b, turn, cast, ep = parse(fen)
    SEEN.append(bkey(b, turn))
    white = turn == "w"
    legal_all = []
    for m in moves(b, turn, cast, ep):
        u = apply(b, m, turn, cast, ep)
        if not attacked(b, king_sq(b, white), not white): legal_all.append(m)
        unapply(b, m, u, turn)
    if not legal_all: return None
    NODES[0] = 0
    best = None
    for d in range(1, 6):
        a = -99999; cur = None; done = True
        for m in legal_all:
            u = apply(b, m, turn, cast, ep)
            k = bkey(b, "b" if turn == "w" else "w")
            v = -search(b, "b" if turn == "w" else "w", u[5], u[6], d - 1, -99999, -a)
            unapply(b, m, u, turn)
            if SEEN[:-1].count(k) >= 1: v -= 120
            if v > a: a = v; cur = m
            if NODES[0] > BUDGET: done = False; break
        if done and cur: best = cur
        if not done or a > 29000: break
    return best

while True:
    g = post("/game", {})
    if g.get("status") == "done": break
    mv = best_move(g["fen"])
    if mv is None: break
    uci = sq_of(mv[0]) + sq_of(mv[1]) + (mv[2] or "")
    r = post("/move", {"game": g["game"], "move": uci})
    if r.get("status") == "done": break
