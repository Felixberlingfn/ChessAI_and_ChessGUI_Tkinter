def convert_to_fen(chessboard, turn='w'):
    # turn = 'w' for white or 'b' for black
    # Create an empty board representation
    rows = [""] * 8

    # Populate the board representation with pieces from the dictionary
    for row in range(1, 9):
        for col in "abcdefgh":
            piece = chessboard[col + str(row)]
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
