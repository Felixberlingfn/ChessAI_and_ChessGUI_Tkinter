import tkinter as tk
from tkinter import ttk
from copy import deepcopy
import chess
import random


def run(info = "This only runs if not imported as a module"):
    def on_chess_move(event):
        # Retrieve the move data from the ChessBoard instance
        start_pos, end_pos, chess_board_object, playing_against_ai = event.widget.move_data

        print(start_pos, end_pos, chess_board_object, playing_against_ai)

        if playing_against_ai == False:
            print("human vs human, nothing to do here")
            return

        if playing_against_ai == True:
            if not chess_board_object.is_game_over():
                print("test")
                legal_moves = list(chess_board_object.legal_moves)
                print(legal_moves)
                # Choose a random move from the list of legal moves
                random_move = random.choice(legal_moves)
                chess_board_object.push(random_move)
                app.update_board(chess_board_object, True)
                """app hass to be created in scope"""
            else:
                print("game is over")



    print(info)
    app = ChessBoard()
    app.start_game()
    chess_board_object = chess.Board()
    app.update_board(chess_board_object)
    app.bind("<<ChessMove>>", on_chess_move)

    # Configure tk style
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 12), borderwidth=0,
                    foreground='MidnightBlue', background='MidnightBlue', relief='flat')

    style.map('TButton',
              foreground=[('pressed', 'MidnightBlue'), ('active', 'MidnightBlue')],
              background=[('!pressed', 'MidnightBlue'), ('active', 'MidnightBlue')],
              relief=[('pressed', 'flat'), ('!pressed', 'flat')])

    app.mainloop()

def help():
    print("""
    Usage:
    """)



def push_human_move(chess_board_object, prev_clicked_square, now_clicked_square):
    move_uci = prev_clicked_square + now_clicked_square
    move = ""
    try:
        move = chess.Move.from_uci(move_uci)
    except:
        print("push_human_move: not valid uci")
    if move not in chess_board_object.legal_moves:
        return False
    chess_board_object.push(move)
    return chess_board_object

class ChessBoard(tk.Tk):
    def __init__(self, chess_board_object = None, dead = None, schachbrett = False, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.state('zoomed')
        self.title("Chess TK")
        self.chess_board_object = chess_board_object
        self.black_square_color = "burlywood" #"dimgray" #burlywood
        self.white_square_color = "snow" #lightgray" #snow
        self.piece_color = {"black": "black", "white":"dimgray", "":""}

        self.chess_font = ("Arial", 48, "bold")

        self.highlight_rectangle = None
        self.red_highlight_rectangle = None
        self.clicked_square = None
        self.turn = "white"
        self.flip = "white_bottom"
        self.playing_against_computer = True
        self.schachbrett = schachbrett
        self.flipped_schachbrett = {}
        self.update_zoom(1.5)

        self.dead = dead
        self.canvas = tk.Canvas(self, width=770, height=850)
        self.canvas.pack()

        #self.create_chessboard()
        #self.add_labels()
        #self.add_pieces()

        self.error_label = tk.Label(self, text="White begins", fg="dimgray")
        self.error_label.pack()
        self.error_label2 = tk.Label(self, text="", fg="red")
        self.error_label2.pack()

        self.message_ai_label = tk.Label(self, text="", fg="black")
        self.message_ai_label.pack()

        """self.zoom_button = ttk.Button(self, text="♛ Zoom 1.5 X", command=lambda: self.update_zoom(1))
        self.zoom_button.place(x=10, y=340)"""

        self.flip_button = ttk.Button(self, text="🗘 FLIP BOARD", command=self.flip_board)
        self.flip_button.place(x=10, y=340)

        self.undo_button = ttk.Button(self, text="⏪ UNDO MOVE", command=lambda: self.undo_move())
        self.undo_button.place(x=10, y=380)

        self.new_game_button = ttk.Button(self, text="🆕 NEW GAME", command=lambda: self.start_game("white", False))
        self.new_game_button.place(x=10, y=420)

        self.save_game_button = ttk.Button(self, text="⬇️ SAVE GAME", command=lambda: self.trigger_moved_event("start_pos", "end_pos", self.chess_board_object, "save_game"))
        self.save_game_button.place(x=10, y=460)

        self.make_stockfish_move_button = ttk.Button(self, text="🐠 Make a Stockfish move", command=lambda: self.trigger_moved_event("start_pos", "end_pos", self.chess_board_object, "make_stockfish_move"))
        self.make_stockfish_move_button.place(x=10, y=260)

        self.lc0_vs_stockfish_button = ttk.Button(self, text="0 lc0 vs stockfish", command=lambda: self.trigger_moved_event("start_pos", "end_pos", self.chess_board_object, "lc0_vs_stockfish"))
        self.lc0_vs_stockfish_button.place(x=10, y=220)

        self.ai_vs_stockfish_button = ttk.Button(self, text="🤖 My ai vs. stockfish (slow)", command=lambda: self.trigger_moved_event("start_pos", "end_pos", self.chess_board_object, "myai_vs_stockfish"))
        self.ai_vs_stockfish_button.place(x=10, y=180)

        self.restart_button = ttk.Button(self, text="🤖 Play My AI (slow)", command=lambda: self.start_game("white", "custom_ai"))
        self.restart_button.place(x=10, y=100)

        self.restart_button2 = ttk.Button(self, text="♛ Play Human", command=lambda: self.start_game("white", False))
        self.restart_button2.place(x=10, y=60)

        self.play_stockfish_button = ttk.Button(self, text="🐠 Play Stockfish", command=lambda: self.start_game("white", "play_stockfish"))
        self.play_stockfish_button.place(x=10, y=20)

        self.add_details()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.style = ttk.Style(self)
        self.configure_styles()

        if chess_board_object:
            self.start_game()
            self.update_board(chess_board_object)


    def update_zoom(self, zoom = 1.5):
        self.zoom = zoom
        self.int_15 = int(15 * zoom)
        self.int_30 = int(30 * zoom)
        self.int_60 = int(60 * zoom)
        self.int_90 = int(90 * zoom)
        self.int_525 = int(525 * zoom)
        self.int_510 = int(510 * zoom)

        #self.create_chessboard()
        #self.add_labels()
        #self.add_pieces()


    def handle_move_by_ai(self):
        try:
            last_move = self.chess_board_object.peek()  # This looks at the last move in the move stack without removing it
            last_move_uci = last_move.uci()  # Convert the move to UCI format
            self.handle_red_outlining()
        except:
            print("No move made yet")


    def handle_last_move(self):
        pass



    def trigger_moved_event(self, start_pos, end_pos, chess_board_object, playing_against_ai = False):
        # Instead of directly handling the move, we generate an event
        self.move_data = (start_pos, end_pos, chess_board_object, playing_against_ai)
        #self.event_generate("<<ChessMove>>", data=(start_pos, end_pos))
        self.event_generate("<<ChessMove>>")


    def on_canvas_click(self, event):
        #self.error_label.config(text="")
        self.error_label2.config(text="")

        x, y = event.x, event.y
        now_clicked_square = self.get_clicked_square_from_x_y(x, y)

        prev_clicked_square = self.clicked_square

        if prev_clicked_square and now_clicked_square:
            valid_move = self.handle_potential_move(prev_clicked_square, now_clicked_square)
            if valid_move:
                self.handle_red_outlining()
                self.trigger_moved_event(prev_clicked_square, now_clicked_square, self.chess_board_object,
                                         self.playing_against_computer)
                return

        self.handle_potential_selection(x, y, prev_clicked_square, now_clicked_square)


    def handle_potential_move(self, prev_clicked_square, now_clicked_square):
        prev_abbr = self.schachbrett[prev_clicked_square]
        capture_abbr = self.schachbrett[now_clicked_square]
        """HERE WE DO THE ONLY CALL TO PROPER GAME LOGIC"""
        returned_chess_board_object_if_valid = push_human_move(self.chess_board_object, prev_clicked_square,
                                                               now_clicked_square)
        """HERE WE DO THE ONLY CALL TO PROPER GAME LOGIC"""
        if returned_chess_board_object_if_valid:
            self.update_board(returned_chess_board_object_if_valid)
            moved_message = f"{get_color(prev_abbr)} moved {get_emoji(prev_abbr)} from {prev_clicked_square} to {now_clicked_square}"
            if capture_abbr != "-":
                moved_message = moved_message + f" and captured {get_emoji(capture_abbr)}"
            #self.error_label.config(text=moved_message, fg="green")
            #self.display_message(moved_message)

            return True
        return False


    def handle_potential_selection(self, x, y, prev_clicked_square, now_clicked_square):
        selection_error = self.check_if_valid_selection(now_clicked_square)
        if selection_error:
            self.display_message(selection_error)
            return
        self.clicked_square = now_clicked_square
        selection_message = f"{get_color(self.schachbrett[now_clicked_square])} selected {get_emoji(self.schachbrett[now_clicked_square])} on {now_clicked_square}"
        self.display_message(selection_message)

        """if self.highlight_rectangle:
            self.canvas.delete(self.highlight_rectangle)"""

        self.canvas.delete("yellow_outline")

        if self.flip != "black_bottom":
            # Draw a highlight rectangle on the clicked square
            col = (x - self.int_30) // self.int_60
            row = (y - self.int_30) // self.int_60
            x1 = col * self.int_60 + self.int_30
            y1 = row * self.int_60 + self.int_30
            x2 = x1 + self.int_60
            y2 = y1 + self.int_60
            self.canvas.delete("yellow_outline")
            self.highlight_rectangle = self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow",
                                                                    tags="yellow_outline", width=3)
        else:
            self.canvas.delete("yellow_outline")
            self.canvas.itemconfig(prev_clicked_square, outline="black", width=1)
            self.canvas.itemconfig(now_clicked_square, outline="yellow", width=3)

    def handle_red_outlining(self):
        try:
            self.remove_all_outlining()

            last_move = self.chess_board_object.peek()
            last_move_uci = last_move.uci()

            print(f"Moved {last_move_uci}")
            #self.display_message(last_move_uci, "green", 12)

            last_move_destination = last_move_uci[2:]

            if self.flip == "black_bottom":
                self.canvas.itemconfig(last_move_destination, outline="red", width=3)
            else:
                self.canvas.itemconfig("default_"+last_move_destination, outline="red", width=3)

        except:
            print("No move made yet")

        # force mainloop update
        self.update()


    def remove_all_outlining(self):
        # remove any red outlines
        for key in self.schachbrett:
            try:
                self.canvas.itemconfig(key, outline="black", width=1)
            except:
                pass
            try:
                self.canvas.itemconfig("default_" + key, outline="black", width=1)
            except:
                pass
        try:
            self.canvas.delete("red_outline")
        except:
            pass

        # remove any yellow outlines
        try:
            self.canvas.delete("yellow_outline")
            self.canvas.delete(self.highlight_rectangle)
        except:
            pass

        # force mainloop update
        self.update()


    def get_clicked_square_from_x_y(self, x, y):
        col = (x - self.int_30) // self.int_60
        row = (y - self.int_30) // self.int_60

        file, rank = "", ""
        # Calculate the chess board coordinates
        if self.flip == "white_bottom":
            file = "abcdefgh"[col]
            rank = 8 - row

        if self.flip == "black_bottom":
            file = "hgfedcba"[col]  # Reverse the order of files
            rank = 1 + row  # Start from 1 at the bottom row

        now_clicked_square = f"{file}{rank}"

        return now_clicked_square



    def configure_styles(self):
        # Configure the ttk styles you want to use
        self.style.configure('TButton', font=('Helvetica', 12), borderwidth=0,
                             foreground='MidnightBlue', background='MidnightBlue', relief='flat')
        self.style.map('TButton',
                       foreground=[('pressed', 'MidnightBlue'), ('active', 'MidnightBlue')],
                       background=[('!pressed', 'MidnightBlue'), ('active', 'MidnightBlue')],
                       relief=[('pressed', 'flat'), ('!pressed', 'flat')])


    def display_message(self, message = "The computer is thinking", label = "label1", color = "green", size = 12):
        if label == "label1":
            self.error_label.config(text=message, fg=color, font=("Helvetica", size, "bold"))
        elif label == "label2":
            self.error_label2.config(text=message, fg=color, font=("Helvetica", size, "bold"))
        else:
            self.message_ai_label.config(text=message, fg=color, font=("Helvetica", size, "bold"))
        # force mainloop update
        self.update()

    def update_board(self, chess_board_object = False, ai = False):
        uci_piece_map = False
        if chess_board_object:
            piece_map = chess_board_object.piece_map()
            uci_piece_map = {chess.square_name(square): piece.symbol() for square, piece in piece_map.items()}
            self.chess_board_object = chess_board_object

        if uci_piece_map != False:
            for key in self.schachbrett:
                self.schachbrett[key] = "-"
            for key, value in uci_piece_map.items():
                if len(key) > 1:
                    self.schachbrett[key] = value

        if self.chess_board_object.turn == chess.WHITE:
            self.turn = "white"
        else:
            self.turn = "black"


        if self.flip == "black_bottom":
            flipped = {}
            file_map = {'a': 'h', 'b': 'g', 'c': 'f', 'd': 'e', 'e': 'd', 'f': 'c', 'g': 'b',
                        'h': 'a'}  # Map for flipping files
            for key, value in self.schachbrett.items():
                file, rank = key  # 'file' gets the letter, 'rank' gets the number
                new_file = file_map[file]  # Flip the file
                new_rank = str(9 - int(rank))  # Calculate the flipped rank
                new_key = new_file + new_rank  # Construct the new key
                flipped[new_key] = value
            self.flipped_schachbrett = deepcopy(flipped)

            self.canvas.delete("pieces")  # Delete all items tagged with "pieces"
            self.add_pieces(flip=True)  # Redraw pieces
            self.add_labels(flip=True)
        else:
            self.canvas.delete("pieces")  # Delete all items tagged with "pieces"
            self.add_pieces()  # Redraw pieces
            if self.highlight_rectangle:
                self.canvas.delete(self.highlight_rectangle)
            if self.clicked_square:
                self.clicked_square = None

        if ai == True:
            self.handle_move_by_ai()
        self.update() # this is a tkinter function


    def create_chessboard(self):
        files = 'abcdefgh'  # Files labeled from a to h
        #ranks = '87654321'  # Ranks labeled from 8 to 1
        color = "white"
        for i in range(8):
            for j in range(8):

                rank_default = 8 - i
                file_default = files[j]
                chess_notation_tag_default = f"{file_default}{rank_default}"


                # Convert the column index to file ('h'-'a') for rotated board
                file = files[7-j]
                rank = i + 1  # Rank is labeled from '1' to '8' from top to bottom
                chess_notation_tag = f"{file}{rank}"

                if color == "white":
                    self.canvas.create_rectangle(j * self.int_60 + self.int_30, i * self.int_60 + self.int_30, j * self.int_60 + self.int_90, i * self.int_60 + self.int_90, tags = (chess_notation_tag, "default_"+chess_notation_tag_default), fill=self.white_square_color)
                    color = "black"
                else:
                    self.canvas.create_rectangle(j * self.int_60 + self.int_30, i * self.int_60 + self.int_30, j * self.int_60 + self.int_90, i * self.int_60 + self.int_90, tag = (chess_notation_tag, "default_"+chess_notation_tag_default), fill=self.black_square_color)
                    color = "white"
            if color == "white":
                color = "black"
            else:
                color = "white"

    def add_labels(self, flip=False):
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        numbers = ['8', '7', '6', '5', '4', '3', '2', '1']

        if flip:
            letters.reverse()  # Reverse the order of the letters
            numbers.reverse()  # Reverse the order of the numbers

        for i, letter in enumerate(letters):
            self.canvas.create_text((i * self.int_60) + self.int_60, self.int_525, text=letter, tags="labels", font=("Arial", 14, "bold"))
            self.canvas.create_text((i * self.int_60) + self.int_60, self.int_15, text=letter, tags="labels", font=("Arial", 14, "bold"))

        for i, number in enumerate(numbers):
            self.canvas.create_text(self.int_15, (i * self.int_60) + self.int_60, text=number, tags="labels", font=("Arial", 14, "bold"))
            self.canvas.create_text(self.int_525, (i * self.int_60) + self.int_60, text=number, tags="labels", font=("Arial", 14, "bold"))

    def add_pieces(self, flip = False):
        if self.flip == "black_bottom":
            use_this_schachbrett = self.flipped_schachbrett
        else:
            use_this_schachbrett = self.schachbrett

        for rank in range(8, 0, -1):
            for index, file in enumerate("abcdefgh"):
                position = f"{file}{rank}"
                self.canvas.create_text(self.int_60 * (index + 1), self.int_60 * abs(rank - 9),
                                        text=get_emoji(use_this_schachbrett[position]),
                                        tags="pieces",
                                        font=self.chess_font, fill=style_color(use_this_schachbrett[position]))
        self.canvas.create_text(self.int_60 * (4), self.int_60 * 9.5,
                                text=self.dead["black"],
                                tags="pieces",
                                font=self.chess_font, fill=style_color("p"))
        self.canvas.create_text(self.int_60 * (4), self.int_60 * 10,
                                text=self.dead["white"],
                                tags="pieces",
                                font=self.chess_font, fill=style_color("P"))


    def check_if_valid_selection(self, now_sq):
        if self.schachbrett[now_sq] == "-":
            return "no piece to select here"
        if get_color(self.schachbrett[now_sq]) != self.turn:
            return f"It's {self.turn}'s turn"
        return False


    def toggle_turn(self):
        self.error_label2.config(text="The computer is thinking ... 💭", fg="black")
        self.update_board()

    def move(self, from_sq, to_sq):
        if self.flip != "black_bottom":
            # highlight the last move in red
            x1, y1, x2, y2 = self.chess_position_to_rectangle_coords(to_sq)
            self.canvas.delete("red_outline")
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="red_outline", width=3)
        else:
            self.canvas.delete("red_outline")

    def start_game(self, color = "white", ai = True):
        self.chess_board_object = chess.Board()
        if self.flip == "black_bottom":
            self.flip = "white_bottom"
        self.playing_against_computer = ai
        # Reset board to initial state
        self.schachbrett = {
            "a1": "R", "b1": "N", "c1": "B", "d1": "Q", "e1": "K", "f1": "B", "g1": "N", "h1": "R",
            "a2": "P", "b2": "P", "c2": "P", "d2": "P", "e2": "P", "f2": "P", "g2": "P", "h2": "P",
            "a3": "-", "b3": "-", "c3": "-", "d3": "-", "e3": "-", "f3": "-", "g3": "-", "h3": "-",
            "a4": "-", "b4": "-", "c4": "-", "d4": "-", "e4": "-", "f4": "-", "g4": "-", "h4": "-",
            "a5": "-", "b5": "-", "c5": "-", "d5": "-", "e5": "-", "f5": "-", "g5": "-", "h5": "-",
            "a6": "-", "b6": "-", "c6": "-", "d6": "-", "e6": "-", "f6": "-", "g6": "-", "h6": "-",
            "a7": "p", "b7": "p", "c7": "p", "d7": "p", "e7": "p", "f7": "p", "g7": "p", "h7": "p",
            "a8": "r", "b8": "n", "c8": "b", "d8": "q", "e8": "k", "f8": "b", "g8": "n", "h8": "r",
        }
        self.dead = {"black": [], "white": []}
        self.king_positions = {"white": "e1", "black": "e8"}
        self.king_has_moved = {"white": False, "black": False}
        self.turn = "white"
        self.clicked_square = None

        self.remove_all_outlining()

        self.create_chessboard()
        self.add_labels()
        self.add_pieces()

        self.error_label.config(text="Game Started. White begins", fg="dimgray")
        self.error_label2.config(text="", fg="red")


    def prettyprint_chessboard(self, the_board):
        for row in range(8, 0, -1):
            for col in 'abcdefgh':
                print(the_board[col + str(row)], end=' ')
            print("")  # New line after each row
        print("-------------")


    def chess_position_to_rectangle_coords(self, chess_position):
        # Mapping the file (column) to its index
        file_to_index = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

        # Extract the file and rank from the chess position
        file = chess_position[0]
        rank = int(chess_position[1])

        # Convert the file and rank to column and row
        col = file_to_index[file]
        row = 8 - rank

        # Convert the column and row to pixel coordinates
        x1 = col * self.int_60 + self.int_30
        y1 = row * self.int_60 + self.int_30
        x2 = x1 + self.int_60
        y2 = y1 + self.int_60

        return x1, y1, x2, y2

    def flip_board(self):
        # remove highlights because they won't make sense in a flipped board (alternatively recreate them)
        self.remove_all_outlining()

        flipped = {}
        file_map = {'a': 'h', 'b': 'g', 'c': 'f', 'd': 'e', 'e': 'd', 'f': 'c', 'g': 'b',
                    'h': 'a'}  # Map for flipping files
        for key, value in self.schachbrett.items():
            file, rank = key  # 'file' gets the letter, 'rank' gets the number
            new_file = file_map[file]  # Flip the file
            new_rank = str(9 - int(rank))  # Calculate the flipped rank
            new_key = new_file + new_rank  # Construct the new key
            flipped[new_key] = value
        self.flipped_schachbrett = flipped

        self.canvas.delete("labels")
        if self.flip == "white_bottom":
            self.add_labels(flip=True)
            self.flip = "black_bottom"
        else:
            self.add_labels(flip=False)
            self.flip = "white_bottom"

        self.update_board()

    def undo_move(self, chess_board_object = None):
        print("undo move")
        if chess_board_object:
            try:
                chess_board_object.pop()
            except:
                print("nothing to undo")
            self.remove_all_outlining()
            self.handle_red_outlining()
            self.update_board(chess_board_object)
        else:
            try:
                self.chess_board_object.pop()
            except:
                print("nothing to undo")
            self.remove_all_outlining()
            self.handle_red_outlining()
            self.update_board(self.chess_board_object)
            self.update()

    def add_details(self):
        self.canvas.create_rectangle(self.int_30, self.int_30, self.int_510, self.int_510, width=2)  # Adding border to the board



def get_emoji(abbr):
    abbr_to_emoji = {
        "K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟",
        "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
    }
    return abbr_to_emoji.get(abbr, "")

def get_name(abbr):
    abbr_to_name = {
        "K": "King", "Q": "Queen", "R": "Rook", "B": "Bishop", "N": "Knight", "P": "Pawn",
    }
    return abbr_to_name.get(abbr.upper(), "")

def get_color(abbr):
    if abbr.islower():
        return "black"
    else:
        return "white"

def get_chess_COLOR(abbr):
    if abbr.islower():
        return chess.BLACK
    else:
        return chess.WHITE

def style_color(abbr):
    if abbr.islower():
        return "black"
    else:
        #return "snow" #"dimgray"
        #return "deeppink"
        #return "midnightblue"
        return "crimson"


if __name__ == '__main__':
    run()
