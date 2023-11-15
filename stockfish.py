import chess
import chess.engine

STOCKFISH_PATH = "stockfish/stockfish-windows-x86-64-avx2.exe"


def stockfish(board, time_limit=0.1):

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    result = engine.play(board, chess.engine.Limit(time=time_limit))

    engine.quit()

    return result.move
