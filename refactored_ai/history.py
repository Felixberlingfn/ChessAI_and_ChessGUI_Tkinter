from chess import square_name

# Initialize the history table or previously successful moves (64x64 from to)
table = [[0 for _ in range(64)] for _ in range(64)]


def update(from_square, to_square, depth):
    table[from_square][to_square] += depth ** 2  # Weight by depth squared


def print_top(top_n=10):
    move_scores = []
    for from_square in range(64):
        for to_square in range(64):
            score = table[from_square][to_square]
            if score > 0:
                move_scores.append(((from_square, to_square), score))

    # Sort the moves by score in descending order
    move_scores.sort(key=lambda x: x[1], reverse=True)

    # Print the top 'n' moves
    for i in range(min(top_n, len(move_scores))):
        from_sq = square_name(move_scores[i][0][0])
        to_sq = square_name(move_scores[i][0][1])
        print(f"{from_sq}{to_sq} has {move_scores[i][1]} Beta cutoffs")
