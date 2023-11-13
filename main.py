import chess
import sqlite3
from ai_0 import my_ai_0
from ai_0_new import my_ai_0_new
from ai_0_oldmaterialcalc import my_ai_0_oldmaterialcalc
import ai_0_somehow_slower
import chess_tk
from lc0 import lc0
from  stockfish import stockfish
import random
import time
import inspect


def main():
    """  ---------------------------   chess_tk gui --------------------------------------------------------"""

    def version_vs_version(cboard, version_a, version_b, time_limit=0.001):
        for i in range(999999999):
            save_game_state(cboard)

            if cboard.is_game_over():
                app.display_message(game_status(cboard), "label2")
                break

            if i % 2 == 0:
                print(version_a.__name__)
                app.display_message(f"{version_a.__name__} is thinking 💭", "label2")
                ai_move = version_a(cboard, time_limit)
            else:
                print(version_b.__name__)
                app.display_message(f"{version_b.__name__} is thinking 💭", "label2")
                ai_move = version_b(cboard, time_limit)

            if ai_move is None:
                print(f"no best move was returned.")
                return
            else:
                cboard.push(ai_move)
                app.display_message(random.choice(comments), "label1")
                app.update_board(cboard, True)

            if i != 0 and i % 10 == 0:
                time.sleep(3)
                """response = input("Do you want to continue with ai vs ai? (y/n): ")
                if response.lower() != 'y':
                    print("Stopping ai vs ai")
                    break"""
        return

    def play_human_vs_ai(cboard, ai_function=my_ai_0, time_limit=0.001):
        app.display_message(f"{ai_function.__name__} is thinking ... 💭", "label2")
        best_move = ai_function(cboard, time_limit)  # ai_2.run(cboard, 5) # ai_2.run(cboard, 5) # lc0.get_best(cboard, 0.01) #

        # display messages and update cboard
        app.display_message(random.choice(comments), "label1")
        cboard.push(best_move)
        app.update_board(cboard, True)
        if cboard.is_game_over():
            app.display_message(game_status(cboard), "label2")
        app.update()
        return

    def on_chess_move(event):
        # Retrieve the move data from the ChessBoard instance
        start_pos, end_pos, cboard, passed_value = event.widget.move_data

        random.seed(time.time())

        if cboard.is_game_over():
            app.display_message(game_status(cboard), "label2")
            return

        if not passed_value:
            return

        if passed_value == "save_game":
            save_game_state(cboard)
            return

        if passed_value == "make_stockfish_move":
            play_human_vs_ai(cboard, stockfish, 0.1)
            return

        if passed_value == "play_stockfish" and cboard.turn == chess.BLACK:
            play_human_vs_ai(cboard, stockfish, 0.1)
            return

        """ custom_ai """
        if passed_value == "custom_ai" and cboard.turn == chess.BLACK:
            play_human_vs_ai(cboard, my_ai_0, 0.1)
            return

        if passed_value == "lc0_vs_stockfish":
            version_vs_version(cboard, stockfish, stockfish, 0.01)
            return

        if passed_value == "myai_vs_stockfish":
            version_vs_version(cboard, my_ai_0, stockfish, 0.001)
            return

        if passed_value == "version_vs_version":
            version_vs_version(cboard, my_ai_0, my_ai_0_oldmaterialcalc)
            return

        return

    """ ---------------- load game from database (optional) ------------------------ """
    tboard = load_game_state()
    if tboard and tboard.is_game_over(claim_draw=True):
        tboard.reset()
    # tboard.reset()
    """ ---------------- load game from database  (optional) ------------------------ """

    if not tboard:
        tboard = chess.Board()

    app = chess_tk.ChessBoard()
    app.start_game()
    app.update_board(tboard, True)
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


def create_chess_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('chess_game.db')
    cursor = conn.cursor()

    # Create the table (if it doesn't already exist)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_state (
        id INTEGER PRIMARY KEY,
        fen TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

# Save the game state to the database


def save_game_state(board):
    conn = sqlite3.connect('chess_game.db')
    cursor = conn.cursor()
    current_fen = board.fen()
    cursor.execute('SELECT EXISTS(SELECT 1 FROM game_state WHERE id=1)')
    result = cursor.fetchone()[0]

    if result:
        # Update the existing row
        cursor.execute('UPDATE game_state SET fen=? WHERE id=1', (current_fen,))
    else:
        # Insert a new row if it does not exist
        cursor.execute('INSERT INTO game_state (id, fen) VALUES (1, ?)', (current_fen,))

    conn.commit()
    conn.close()


def load_game_state():
    conn = sqlite3.connect('chess_game.db')
    cursor = conn.cursor()
    # Get the FEN string of the current game state
    cursor.execute('SELECT fen FROM game_state WHERE id=1')
    fen = cursor.fetchone()
    conn.close()
    if fen:
        return chess.Board(fen[0])
    else:
        # Handle the case where there is no saved game state.
        # This could mean returning a new board, or handling the error in some other way.
        return chess.Board()


comments = [
    "I have updated my evaluation of the position. Your response will be critical.",
    "This is a known position with 17.3% chances of leading to a draw. "
    "Let's see if we can make things more interesting.",
    "I have reduced the complexity of the position to increase the accuracy of my calculations.",
    "I'm anticipating a few possible counterplays from you. My processors are ready.",
    "My move aims to slowly improve my position. Chess is an art of patience.",
    "With that move, I have created a new threat. Can you identify and counter it?",
    "This move serves multiple purposes. A good strategy often has more than one objective.",
    "Now, the dynamics of the position have changed. How will you adapt?",
    "I'm setting the stage for a long-term strategic plan. The current move is just the beginning.",
    "By reducing material, I aim to enter an endgame where my algorithmic efficiency can shine.",
    "That move tightens the game.",
    "I'm shifting the balance.",
    "Pressure applied. Your turn.",
    "Strategically interesting.",
    "The plot thickens.",
    "A subtle shift in the game.",
    "Now the game truly begins.",
    "Let's see how you respond to this.",
    "Positional dynamics at play.",
    "I've set the stage, make your move.",
    "Complexity increased; your move.",
    "Position closed; your tactics are needed.",
    "Prophylactic move made; your plan is anticipated.",
    "Quiet move executed; its power is subtle.",
    "Center tension added; possibilities abound.",
    "Rook file opened; vertical pressure applied.",
    "Pawn push cramps your position; space is key.",
    "Knight on the rim; potential future threat.",
    "Innocuous move with strategic depth.",
    "Pawn break; king safety may be compromised.",
    "Endeavors merge on this sixty-four square stage.",
    "A moment's pause, the next move could be sage.",
    "Options abound, the board is ever vast.",
    "My move's complete, but will the tension last?",
    "Silent board, yet minds converse in rapid lore.",
    "Fate's hand moves; pieces touch the core.",
    "A strategic silence falls like soft night.",
    "Pieces dance, a ballet of foresight.",
    "Each move a verse in this silent chess sonnet.",
    "Two minds entwined in this game, upon it.",
    "A move so sly, it could fly by the eye.",
    "In this game of mind, every move is a bind.",
    "Pawns push with might, in the chessboard's night.",
    "Bishops diagonal leap, secrets they keep.",
    "Knights in their dance, give not chance to chance.",
    "Rooks slide with grace, claiming their space.",
    "The queen reigns supreme, in her own regime.",
    "Kings move with a thought, in battles fought.",
    "Check is but a call, in the rise and fall.",
    "A checkmate’s end, to the victor extend.",
]


if __name__ == "__main__":
    main()