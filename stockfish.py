import chess
import chess.engine

"""
Stockfish level and elo according to forum posts
source 1    source 2    my ai       chess.com elo
1 800       
2 1100
3 1400
4 1700      1600        11.3bb      1400-1750 - 11.3bb 
5 2000      1700        
6 2300      1900
7 2700      2200
8 3000      2600
"""

STOCKFISH_PATH = "stockfish/stockfish-windows-x86-64-avx2.exe"


def stockfish(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 10})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move


def stockfish_1(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 1})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move


def stockfish_2(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 2})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move


def stockfish_3(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 3})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move


def stockfish_4(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 4})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move


def stockfish_5(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 5})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move


def stockfish_6(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 6})

    result = engine.play(board, chess.engine.Limit(depth=20))

    engine.quit()

    return result.move
