import sqlite3
from chess import Board, WHITE


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
        return Board(fen[0])
    else:
        return Board()


