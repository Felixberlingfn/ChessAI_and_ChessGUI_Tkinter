import chess.engine  # testing

STOCKFISH_PATH = "./stockfish/stockfish-windows-x86-64-avx2.exe"  # testing


def stockfish_shallow(board, real_depth):
    if real_depth > 1:
        return 0
    """ this is for testing a concept where you do a static evaluation or very
    shallow search during move ordering to inform what move to investigate first"""

    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

    """ Do a depth 1 search, essentially giving the best move based on static eval"""
    """ This is just to test the effect this might have on move ordering"""
    result = engine.play(board, chess.engine.Limit(depth=1))

    engine.quit()
    """ this is a placeholder before I would implement my own"""

    return result.move


def stockfish_eval(board, depth=0):
    with chess.engine.SimpleEngine.popen_uci('/content/stockfish') as sf:
        result = sf.analyse(board, chess.engine.Limit(depth=depth))
        score = result['score'].white().score()
    return score
