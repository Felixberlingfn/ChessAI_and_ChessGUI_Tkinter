import chess

def convert_dict(board_dict, color = "get_color_from_old_pos", old_position = None, new_position = None):
    # convert to board object (python chess library)
    turn = "w" # default
    if old_position:
        piece_abbr = board_dict[old_position]
        turn = get_fen_color(piece_abbr)
    if color != "get_color_from_old_pos":
        turn = color # w or b
    board_fen = convert_to_fen(board_dict, turn)
    board = chess.Board(board_fen)

    if old_position and new_position:
        try:
            move = chess.Move.from_uci(old_position + new_position)
        except:
            return False
        if move in board.legal_moves:
            board.push(move)
        else:
            return False
    return board



def convert_to_fen(schachbrett, turn = 'w'):
    #turn = 'w' for white or 'b' for black
    # Create an empty board representation
    rows = [""] * 8

    # Populate the board representation with pieces from the dictionary
    for row in range(1, 9):
        for col in "abcdefgh":
            piece = schachbrett[col + str(row)]
            if piece == "-":
                # Add empty squares
                if rows[8 - row]:
                    if rows[8 - row][-1].isdigit():
                        rows[8 - row] = rows[8 - row][:-1] + str(int(rows[8 - row][-1]) + 1)
                    else:
                        rows[8 - row] += '1'
                else:
                    rows[8 - row] += '1'
            else:
                # Add pieces
                rows[8 - row] += piece

    # Join the rows to get the piece placement data
    fen_rows = "/".join(rows)

    # Set up other FEN information - assume standard starting positions for simplicity
    fen = f"{fen_rows} {turn} KQkq - 0 1"

    return fen

def get_fen_color(abbr):
    if abbr == "-":
        return None
    if abbr.islower():
        return "b"
    else:
        return "w"
