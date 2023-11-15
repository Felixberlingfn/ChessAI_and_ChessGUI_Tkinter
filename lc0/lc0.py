import chess
import chess.engine



def lc0(board, time_limit = 0.2):
    LCZERO_PATH = 'lc0.exe'
    NETWORK_PATH = '791556.pb.gz'

    engine = chess.engine.SimpleEngine.popen_uci(LCZERO_PATH)

    engine.configure({"WeightsFile": NETWORK_PATH})

    result = engine.play(board, chess.engine.Limit(time=time_limit))

    engine.quit()

    return result.move



def iterative(board, max_depth):
    best_move = None
    for time_limit in range(1, 4, 1):
        time_limit_s = time_limit / 10
        new_move = lc0(board, time_limit_s)
        if new_move:
            board.push(new_move)
            if board.is_checkmate():
                board.pop()
                return best_move
            board.pop()
            best_move = new_move
    return best_move


if __name__ == "__main__":
    main()