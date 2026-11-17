#!/usr/bin/env python3
import random, time, chess, engine_v3, os, subprocess, json, http.server, threading

def equivalent(fen):
    bd = chess.Board(fen)
    pos = engine_v3.fen_to_position(fen)
    rt = engine_v3.position_to_fen(pos)
    # Compare a full legal-move tranche, which also checks castling/ep/kp.
    moves_bd = [m.uci() for m in bd.legal_moves]
    moves_pos = [engine_v3.to_uci(m, bd.turn == chess.BLACK) for m in pos.gen_moves()]
    assert set(moves_bd) == set(moves_pos), (fen, rt, moves_bd, moves_pos)
    # Make the same moves and compare all resulting fen-derived fields.
    for uci in moves_bd:
        m = chess.Move.from_uci(uci)
        bd2 = bd.copy(); bd2.push(m)
        sm = engine_v3.to_sunfish(uci, bd.turn == chess.BLACK)
        p2 = pos.move(sm)
        moves_bd2 = {m.uci() for m in bd2.legal_moves}
        moves_p2 = {engine_v3.to_uci(m, bd2.turn == chess.BLACK) for m in p2.gen_moves()}
        assert moves_bd2 == moves_p2, (fen, uci, moves_bd2, moves_p2)

def unit_tests():
    board = chess.Board()
    random.seed(123)
    for ply in range(500):
        equivalent(board.fen())
        moves = list(board.legal_moves)
        if not moves or ply >= 180: break
        board.push(random.choice(moves))
    for _ in range(200):
        bd = chess.Board()
        for ply in range(random.randrange(5, 80)):
            equivalent(bd.fen())
            ms = list(bd.legal_moves)
            if not ms: break
            bd.push(random.choice(ms))
    print("conversion tests: OK")

def timed_positions():
    positions = [
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
        "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        "r2q1rk1/pppnbppp/4pnb1/3pP3/2PP4/2N1BN2/PPQ1BPPP/R3K2R w KQ - 0 10",
        "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
        "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
    ]
    times = []
    for fen in positions:
        pos = engine_v3.fen_to_position(fen)
        s = engine_v3.Searcher(); s.node_cap = 50000
        t = time.time(); best = None
        try:
            for depth, gamma, score, move in s.search([pos]):
                if move: best = move
                if s.nodes >= 50000 and best: break
        except engine_v3.Stop: pass
        times.append(time.time() - t)
        assert best, fen
    print("worst move time: %.3fs" % max(times), "| mean %.3fs" % (sum(times)/len(times)))

def fake_env():
    os.makedirs("/tmp/verify3", exist_ok=True)
    # Use fake_env.py directly, capturing its JSON line.
    out = subprocess.run(["python3", "fake_env.py", "engine_v3.py"], capture_output=True, text=True, timeout=1800)
    print(out.stdout.strip())
    assert out.returncode == 0 and "DETERMINISM True" in out.stdout, out.stderr[-2000:]

if __name__ == "__main__":
    unit_tests(); timed_positions(); fake_env()
