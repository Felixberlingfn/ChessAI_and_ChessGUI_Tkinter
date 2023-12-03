import chess
import chess_tk
import random
import time
import db


from stable_ai_v11_3bb import ai_0 as v11_3bb
from stable_ai_v12 import ai_0 as v12
from stable_ai_v12_0 import ai_0 as v12_0
from stable_ai_v12_1 import ai_0 as v12_1
from stable_ai_v13 import ai_0 as v13
from stable_ai_v14_lazy import ai_0 as v14
from stable_ai_v14_startover import ai_0 as v14fix
from stable_ai_v15 import ai_0 as v15
from stable_ai_v15_ONLY_CHANGE_CONFIG import ai_0 as v15_config # is most up to date and works
from stable_ai_v16 import ai_0 as v16 # is v14fix with alpha beta

from stockfish import stockfish, stockfish_6, stockfish_5, stockfish_2, stockfish_3, stockfish_4
from comments import comments
from tournament import run_round_robin_tournament, print_tournament_results
from helpers import determine_winner


ai_player_1 = v13  # White
ai_player_2 = v13  # Black
ai_playing_against_human = v13
ai_playing_against_stockfish = v13

stockfish_level = stockfish_4

""" ai tournament (round robin / everyone against everyone) """
# tuple like [("V11.1", v11_1), ("V11.2", v11_2)] ("V11.2", v11_2),
ai_tournament_vs = [("st.fish lv4", stockfish_4), ("v15 config", v15_config)]  # ("st.fish lv4", stockfish_4) ("V11.2", v11_2)

STOCKFISH_TIME_LIMIT = 0.002  # 2 Milliseconds


""" '.\pypy main.py' is faster but doesn't work with stockfish """


def main():
    """  ---------------------------   chess_tk gui --------------------------------------------------------"""
    def version_vs_version(chess_board, version_a, version_b, time_limit_1=0.001, time_limit_2=0.001):
        for i in range(1000):
            db.save_game_state(chess_board)

            if chess_board.is_game_over():
                result = game_status(chess_board)
                app.display_message(result, "label2")
                print("############################################")
                print(result)
                print("############################################")
                for move in chess_board.move_stack:
                    print(f'"{move.uci()}", ', end="")
                return determine_winner(result, version_a, version_b)

            if i % 2 == 0:
                app.display_message(f"version_a is thinking 💭", "label2")
                ai_move = version_a(chess_board, time_limit_1)
            else:
                app.display_message(f"version_b is thinking 💭", "label2")
                ai_move = version_b(chess_board, time_limit_2)

            if ai_move is None:
                print(f"no best move was returned.")
                return
            else:
                chess_board.push(ai_move)
                app.display_message(random.choice(comments), "label1")
                app.update_board(chess_board, True)

            if i != 0 and i % 10 == 0:
                time.sleep(3)
                """response = input("Do you want to continue with ai vs ai? (y/n): ")
                if response.lower() != 'y':
                    print("Stopping ai vs ai")
                    break"""
        for move in chess_board.move_stack:
            print(f'"{move.uci()}", ', end="")
        return

    def play_human_vs_ai(chess_board, ai_function=ai_playing_against_human, time_limit=30.0):
        app.display_message(f"{ai_function.__name__} is thinking ... 💭", "label2")
        best_move = ai_function(chess_board, time_limit)

        # display messages and update chess_board
        app.display_message(random.choice(comments), "label1")
        chess_board.push(best_move)
        app.update_board(chess_board, True)
        if chess_board.is_game_over():
            app.display_message(game_status(chess_board), "label2")
        app.update()
        return

    def on_chess_move(event):
        # Retrieve the move data from the ChessBoard instance
        start_pos, end_pos, chess_board, passed_value = event.widget.move_data

        random.seed(time.time())

        if chess_board.is_game_over():
            app.display_message(game_status(chess_board), "label2")
            return

        if not passed_value:
            return

        if passed_value == "save_game":
            db.save_game_state(chess_board)
            return

        if passed_value == "make_stockfish_move":
            play_human_vs_ai(chess_board, stockfish, 0.1)
            return

        if passed_value == "play_stockfish" and chess_board.turn == chess.BLACK:
            play_human_vs_ai(chess_board, stockfish_level, 0.1)
            return

        """ custom_ai """
        if passed_value == "custom_ai" and chess_board.turn == chess.BLACK:
            play_human_vs_ai(chess_board, ai_playing_against_human, 30)
            return

        if passed_value == "lc0_vs_stockfish":
            version_vs_version(chess_board, stockfish, stockfish, 0.01)
            return

        if passed_value == "myai_vs_stockfish":
            version_vs_version(chess_board, ai_playing_against_stockfish, stockfish_level, 30, STOCKFISH_TIME_LIMIT)
            return

        if passed_value == "version_vs_version":
            version_vs_version(chess_board, ai_player_1, ai_player_2,  30, 30)
            return

        if passed_value == "tournament":
            tournament_results = run_round_robin_tournament(ai_tournament_vs, chess_board, app, version_vs_version)
            print_tournament_results(tournament_results)
            return

        return

    """ ---------------- load game from database (optional) ------------------------ """
    start_board = db.load_game_state()
    if start_board and start_board.is_game_over(claim_draw=True):
        start_board.reset()
    # start_board.reset()
    """ ---------------- load game from database  (optional) ------------------------ """

    if not start_board:
        start_board = chess.Board()

    app = chess_tk.ChessBoard()
    app.start_game()
    app.update_board(start_board, True)
    app.bind("<<ChessMove>>", on_chess_move)

    """this blocks anything coming after it so everything else is handled in the on_chess_move event 
    bound to the tkinter"""
    app.mainloop()

    """-------------------------------  End of chess_tk gui --------------------------------------------------------"""


def game_status(board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return "Black wins by checkmate"
        else:
            return "White wins by checkmate"
    elif board.is_stalemate():
        return "Draw by stalemate"
    elif board.is_insufficient_material():
        return "Draw due to insufficient material"
    elif board.can_claim_draw():
        return "Draw can be claimed"
    elif board.is_seventyfive_moves():
        return "Draw by 75-move rule"
    elif board.is_fivefold_repetition():
        return "Draw by fivefold repetition"
    else:
        return "Game is not over"

# -----------------------------------------------------------------------


if __name__ == "__main__":
    db.create_chess_database()
    main()
