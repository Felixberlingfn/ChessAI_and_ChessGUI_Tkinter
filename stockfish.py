import chess
import chess.engine

STOCKFISH_PATH = "stockfish/stockfish-windows-x86-64-avx2.exe"


def stockfish(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 10})

    result = engine.play(board, chess.engine.Limit(depth=3))

    engine.quit()

    return result.move


def stockfish_1(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 1})

    result = engine.play(board, chess.engine.Limit(depth=4))

    engine.quit()

    return result.move


def stockfish_2(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 2})

    result = engine.play(board, chess.engine.Limit(depth=4))

    engine.quit()

    return result.move


def stockfish_3(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    engine.configure({"Skill Level": 3})

    result = engine.play(board, chess.engine.Limit(depth=4))

    engine.quit()

    return result.move
