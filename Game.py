import random
import tkinter as tk


EMPTY = ""
PLAYERS = ("X", "O")
LINES = (
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    ((0, 0), (1, 0), (2, 0)),
    ((0, 1), (1, 1), (2, 1)),
    ((0, 2), (1, 2), (2, 2)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


COLOR_SCHEMES = {
    "Red / Blue": {
        "bg": "#10141f",
        "panel": "#171d2b",
        "cell": "#222b3c",
        "cell_alt": "#1a2231",
        "disabled": "#111722",
        "active": "#344563",
        "border": "#0b0f17",
        "grid": "#2f394d",
        "text": "#e9eef8",
        "muted": "#9aa7bd",
        "x": "#ff4f67",
        "o": "#4da3ff",
        "x_win": "#ff4f67",
        "o_win": "#4da3ff",
    },
    "Green / Purple": {
        "bg": "#0d1412",
        "panel": "#151f1c",
        "cell": "#20302c",
        "cell_alt": "#17231f",
        "disabled": "#0e1715",
        "active": "#315447",
        "border": "#08110f",
        "grid": "#395049",
        "text": "#edf8f2",
        "muted": "#9fb6ad",
        "x": "#47f08a",
        "o": "#c46cff",
        "x_win": "#47f08a",
        "o_win": "#c46cff",
    },
    "Cyan / Magenta": {
        "bg": "#0b1118",
        "panel": "#121b25",
        "cell": "#1b2937",
        "cell_alt": "#14202b",
        "disabled": "#0d141c",
        "active": "#24475a",
        "border": "#071018",
        "grid": "#31485a",
        "text": "#ecf7ff",
        "muted": "#98acbc",
        "x": "#22d8ff",
        "o": "#ff4fd8",
        "x_win": "#22d8ff",
        "o_win": "#ff4fd8",
    },
}


def rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = (
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    )
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedCell(tk.Canvas):
    def __init__(self, parent, command, colors):
        super().__init__(
            parent,
            width=48,
            height=48,
            bg=colors["border"],
            highlightthickness=0,
            bd=0,
        )
        self.command = command
        self.colors = colors
        self.text = ""
        self.fill = colors["cell"]
        self.fg = colors["text"]
        self.active_fill = colors["active"]
        self.state = "normal"
        self.rect_id = None
        self.text_id = None
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.draw()

    def draw(self):
        self.delete("all")
        self.rect_id = rounded_rect(
            self,
            3,
            3,
            45,
            45,
            7,
            fill=self.fill,
            outline=self.colors["grid"],
            width=1,
        )
        self.text_id = self.create_text(
            24,
            24,
            text=self.text,
            fill=self.fg,
            font=("Arial", 18, "bold"),
        )

    def config(self, cnf=None, **kwargs):
        if cnf:
            kwargs.update(cnf)
        if "text" in kwargs:
            self.text = kwargs["text"]
        if "bg" in kwargs:
            self.fill = kwargs["bg"]
        if "fg" in kwargs:
            self.fg = kwargs["fg"]
        if "activebackground" in kwargs:
            self.active_fill = kwargs["activebackground"]
        if "state" in kwargs:
            self.state = kwargs["state"]
        if "disabledforeground" in kwargs and self.state == "disabled":
            self.fg = kwargs["disabledforeground"]
        self.draw()

    configure = config

    def on_click(self, _event):
        if self.state != "disabled":
            self.command()

    def on_enter(self, _event):
        if self.state != "disabled" and self.text == "":
            self.itemconfig(self.rect_id, fill=self.active_fill)

    def on_leave(self, _event):
        self.itemconfig(self.rect_id, fill=self.fill)


class RoundedActionButton(tk.Canvas):
    def __init__(self, parent, text, command, colors, width=160):
        super().__init__(
            parent,
            width=width,
            height=42,
            bg=colors["bg"],
            highlightthickness=0,
            bd=0,
        )
        self.command = command
        self.colors = colors
        self.text = text
        self.fill = colors["active"]
        self.hover_fill = colors["cell"]
        self.text_id = None
        self.rect_id = None
        self.bind("<Button-1>", lambda _event: self.command())
        self.bind("<Enter>", lambda _event: self.itemconfig(self.rect_id, fill=self.hover_fill))
        self.bind("<Leave>", lambda _event: self.itemconfig(self.rect_id, fill=self.fill))
        self.draw()

    def draw(self):
        self.delete("all")
        self.rect_id = rounded_rect(
            self,
            2,
            2,
            int(self["width"]) - 2,
            40,
            12,
            fill=self.fill,
            outline=self.colors["grid"],
            width=1,
        )
        self.text_id = self.create_text(
            int(self["width"]) / 2,
            21,
            text=self.text,
            fill=self.colors["text"],
            font=("Arial", 12, "bold"),
        )


class UltimateTicTacToe:
    def __init__(self, root, ai_enabled=True, ai_player="O", search_depth=4):
        self.root = root
        self.root.title("Ultimate Tic Tac Toe")
        self.root.configure(bg=COLOR_SCHEMES["Red / Blue"]["bg"])

        self.ai_enabled = ai_enabled
        self.ai_player = ai_player
        self.search_depth = search_depth
        self.scheme_name = "Red / Blue"
        self.colors = COLOR_SCHEMES[self.scheme_name]

        self.current_player = "X"
        self.next_board = None
        self.ai_thinking = False
        self.game_over = False

        self.boards = []
        self.big_wins = []
        self.buttons = []
        self.board_frames = []
        self.status = None
        self.menu_canvas = None
        self.menu_frame = None
        self.game_frame = None
        self.mode_var = tk.StringVar(value="ai" if ai_enabled else "pvp")
        self.color_var = tk.StringVar(value=self.scheme_name)

        self.show_menu()

    def show_menu(self):
        self.clear_root()
        self.colors = COLOR_SCHEMES[self.color_var.get()]
        self.root.configure(bg=self.colors["bg"])
        self.root.title("Ultimate Tic Tac Toe")

        self.menu_canvas = tk.Canvas(
            self.root,
            width=430,
            height=430,
            bg=self.colors["bg"],
            highlightthickness=0,
            bd=0,
        )
        self.menu_canvas.grid(row=0, column=0, padx=18, pady=18)
        rounded_rect(
            self.menu_canvas,
            4,
            4,
            426,
            426,
            18,
            fill=self.colors["panel"],
            outline=self.colors["grid"],
            width=2,
        )

        self.menu_frame = tk.Frame(
            self.menu_canvas,
            bg=self.colors["panel"],
            padx=0,
            pady=0,
        )
        self.menu_frame.columnconfigure(0, weight=1)
        self.menu_frame.columnconfigure(1, minsize=78)
        self.menu_canvas.create_window(36, 30, anchor="nw", width=358, window=self.menu_frame)

        title = tk.Label(
            self.menu_frame,
            text="Ultimate Tic Tac Toe",
            font=("Arial", 22, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 18), sticky="ew")

        self.add_menu_radio("Player vs AI", "ai", 1)
        self.add_menu_radio("Player vs Player", "pvp", 2)

        palette_label = tk.Label(
            self.menu_frame,
            text="Color scheme",
            font=("Arial", 12, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["muted"],
        )
        palette_label.grid(row=3, column=0, columnspan=2, pady=(22, 8), sticky="w")

        for row, name in enumerate(COLOR_SCHEMES, start=4):
            self.add_color_option(name, row)

        start_button = RoundedActionButton(
            self.menu_frame,
            text="Start Game",
            command=self.start_game,
            colors=self.colors,
            width=350,
        )
        start_button.grid(row=8, column=0, columnspan=2, pady=(24, 0), sticky="w")

    def add_menu_radio(self, text, value, row):
        radio = tk.Radiobutton(
            self.menu_frame,
            text=text,
            variable=self.mode_var,
            value=value,
            font=("Arial", 13),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            selectcolor=self.colors["panel"],
            activebackground=self.colors["panel"],
            activeforeground=self.colors["text"],
        )
        radio.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)

    def add_color_option(self, name, row):
        option_colors = COLOR_SCHEMES[name]
        radio = tk.Radiobutton(
            self.menu_frame,
            text=name,
            variable=self.color_var,
            value=name,
            command=self.show_menu,
            font=("Arial", 12),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            selectcolor=self.colors["panel"],
            activebackground=self.colors["panel"],
            activeforeground=self.colors["text"],
        )
        radio.grid(row=row, column=0, sticky="w", pady=5)

        dots = tk.Frame(self.menu_frame, bg=self.colors["panel"])
        dots.grid(row=row, column=1, sticky="e", padx=(8, 0))
        for i, color in enumerate((option_colors["x"], option_colors["o"])):
            dot = tk.Canvas(
                dots,
                width=18,
                height=18,
                bg=self.colors["panel"],
                highlightthickness=0,
            )
            dot.create_oval(3, 3, 15, 15, fill=color, outline=color)
            dot.grid(row=0, column=i, padx=2)

    def clear_root(self):
        for child in self.root.winfo_children():
            child.destroy()

    def start_game(self):
        self.ai_enabled = self.mode_var.get() == "ai"
        self.colors = COLOR_SCHEMES[self.color_var.get()]
        self.root.configure(bg=self.colors["bg"])
        self.reset_state()
        self.clear_root()

        self.game_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=14, pady=14)
        self.game_frame.grid(row=0, column=0)

        top_bar = tk.Frame(self.game_frame, bg=self.colors["bg"])
        top_bar.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        top_bar.columnconfigure(0, weight=1)

        self.status = tk.Label(
            top_bar,
            text="Player X's turn",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
        )
        self.status.grid(row=0, column=0, sticky="w")

        menu_button = RoundedActionButton(
            top_bar,
            text="Quit to Menu",
            command=self.show_menu,
            colors=self.colors,
            width=130,
        )
        menu_button.grid(row=0, column=1, sticky="e")

        self.create_board()
        self.highlight_active_board()

    def reset_state(self):
        self.current_player = "X"
        self.next_board = None
        self.ai_thinking = False
        self.game_over = False
        self.boards = [[[[EMPTY for _ in range(3)] for _ in range(3)]
                        for _ in range(3)] for _ in range(3)]
        self.big_wins = [[EMPTY for _ in range(3)] for _ in range(3)]
        self.buttons = [[[[None for _ in range(3)] for _ in range(3)]
                         for _ in range(3)] for _ in range(3)]
        self.board_frames = [[None for _ in range(3)] for _ in range(3)]

    def create_board(self):
        for big_r in range(3):
            for big_c in range(3):
                frame = tk.Frame(
                    self.game_frame,
                    bd=0,
                    relief="flat",
                    bg=self.colors["border"],
                    highlightbackground=self.colors["border"],
                    highlightthickness=2,
                )
                frame.grid(row=big_r + 1, column=big_c, padx=7, pady=7)
                self.board_frames[big_r][big_c] = frame

                for r in range(3):
                    for c in range(3):
                        btn = RoundedCell(
                            frame,
                            colors=self.colors,
                            command=lambda br=big_r, bc=big_c, rr=r, cc=c:
                                self.make_move(br, bc, rr, cc)
                        )
                        btn.grid(row=r, column=c, padx=1, pady=1)
                        self.buttons[big_r][big_c][r][c] = btn

    def make_move(self, br, bc, r, c, is_ai_move=False):
        if self.game_over:
            return
        if self.ai_thinking and not is_ai_move:
            return
        if (br, bc, r, c) not in self.get_valid_moves():
            return

        self.place_move(br, bc, r, c, self.current_player)
        self.refresh_cell(br, bc, r, c)

        if self.check_win(self.boards[br][bc]):
            self.big_wins[br][bc] = self.current_player
            self.color_won_board(br, bc, self.current_player)

        if self.check_win(self.big_wins):
            self.game_over = True
            self.status.config(text=f"Player {self.current_player} wins!")
            self.disable_all()
            return

        if self.is_game_draw():
            self.game_over = True
            self.status.config(text="Game is a draw!")
            self.disable_all()
            return

        self.next_board = self.resolve_next_board(r, c)
        self.current_player = "O" if self.current_player == "X" else "X"

        self.update_status()
        self.highlight_active_board()

        if self.ai_enabled and self.current_player == self.ai_player and not is_ai_move:
            self.root.after(250, self.ai_move)

    def place_move(self, br, bc, r, c, player):
        self.boards[br][bc][r][c] = player

    def refresh_cell(self, br, bc, r, c):
        player = self.boards[br][bc][r][c]
        color = self.colors["x"] if player == "X" else self.colors["o"]
        self.buttons[br][bc][r][c].config(
            text=player,
            fg=color,
            bg=self.colors["cell"],
            activebackground=self.colors["cell"],
            disabledforeground=color,
        )

    def resolve_next_board(self, r, c):
        if self.big_wins[r][c] != EMPTY or self.is_full(self.boards[r][c]):
            return None
        return (r, c)

    def color_won_board(self, br, bc, player):
        color = self.colors["x_win"] if player == "X" else self.colors["o_win"]
        fg = self.colors["bg"]

        for r in range(3):
            for c in range(3):
                self.buttons[br][bc][r][c].config(
                    bg=color,
                    fg=fg,
                    activebackground=color,
                    disabledforeground=fg,
                    highlightbackground=self.colors["border"],
                )

    def highlight_active_board(self):
        for br in range(3):
            for bc in range(3):
                active = self.next_board is None or (br, bc) == self.next_board
                for r in range(3):
                    for c in range(3):
                        btn = self.buttons[br][bc][r][c]
                        if self.big_wins[br][bc] != EMPTY:
                            continue

                        player = self.boards[br][bc][r][c]
                        if player != EMPTY:
                            fg = self.colors["x"] if player == "X" else self.colors["o"]
                            btn.config(
                                bg=self.colors["cell"],
                                fg=fg,
                                activebackground=self.colors["cell"],
                                highlightbackground=self.colors["grid"],
                            )
                        elif active:
                            btn.config(
                                bg=self.colors["active"],
                                activebackground=self.colors["active"],
                                highlightbackground=self.colors["grid"],
                                state="normal",
                            )
                        else:
                            btn.config(
                                bg=self.colors["disabled"],
                                activebackground=self.colors["disabled"],
                                highlightbackground=self.colors["grid"],
                                state="normal",
                            )

    def update_status(self):
        mode = "AI" if self.ai_enabled and self.current_player == self.ai_player else "Player"
        if self.next_board:
            row, col = self.next_board
            location = f"local board ({row + 1}, {col + 1})"
        else:
            location = "any open board"
        self.status.config(text=f"{mode} {self.current_player}'s turn: {location}")

    def check_win(self, board):
        return any(board[a[0]][a[1]] == board[b[0]][b[1]] == board[c[0]][c[1]] != EMPTY
                   for a, b, c in LINES)

    def is_full(self, board):
        return all(cell != EMPTY for row in board for cell in row)

    def is_game_draw(self):
        return not self.check_win(self.big_wins) and not self.get_valid_moves()

    def ai_move(self):
        self.ai_thinking = True
        self.status.config(text=f"AI ({self.ai_player}) is thinking...")
        self.root.update()

        best_move = self.choose_ai_move(self.search_depth)
        self.ai_thinking = False

        if best_move:
            self.make_move(*best_move, is_ai_move=True)
        else:
            self.game_over = True
            self.status.config(text="Game is a draw!")

    def choose_ai_move(self, depth=None):
        depth = self.search_depth if depth is None else depth
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None

        best_score = float("-inf")
        best_moves = []

        for move in self.order_moves(valid_moves, self.ai_player):
            undo = self.apply_simulated_move(move, self.ai_player)
            score = self.minimax(depth - 1, float("-inf"), float("inf"), False)
            self.undo_simulated_move(undo)

            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return random.choice(best_moves)

    def order_moves(self, moves, player):
        opponent = "X" if player == "O" else "O"
        move_scores = []

        for move in moves:
            br, bc, r, c = move
            score = 0

            undo = self.apply_simulated_move(move, player)
            if self.has_three_in_a_row(self.big_wins, player):
                score += 10000
            elif self.big_wins[br][bc] == player:
                score += 500
            self.undo_simulated_move(undo)

            undo = self.apply_simulated_move(move, opponent)
            if self.has_three_in_a_row(self.big_wins, opponent):
                score += 9000
            elif self.big_wins[br][bc] == opponent:
                score += 350
            self.undo_simulated_move(undo)

            if (br, bc) == (1, 1):
                score += 30
            if (r, c) == (1, 1):
                score += 10
            if self.big_wins[r][c] != EMPTY or self.is_full(self.boards[r][c]):
                score -= 40

            move_scores.append((score, move))

        move_scores.sort(reverse=True, key=lambda item: item[0])
        return [move for _, move in move_scores]

    def get_valid_moves(self):
        valid_moves = []
        target = self.next_board

        if target is not None:
            br, bc = target
            if self.big_wins[br][bc] != EMPTY or self.is_full(self.boards[br][bc]):
                target = None

        if target is None:
            for br in range(3):
                for bc in range(3):
                    if self.big_wins[br][bc] == EMPTY and not self.is_full(self.boards[br][bc]):
                        for r in range(3):
                            for c in range(3):
                                if self.boards[br][bc][r][c] == EMPTY:
                                    valid_moves.append((br, bc, r, c))
        else:
            br, bc = target
            for r in range(3):
                for c in range(3):
                    if self.boards[br][bc][r][c] == EMPTY:
                        valid_moves.append((br, bc, r, c))

        return valid_moves

    def minimax(self, depth, alpha, beta, is_maximizing):
        opponent = "X" if self.ai_player == "O" else "O"

        if self.has_three_in_a_row(self.big_wins, self.ai_player):
            return 10000000 + depth
        if self.has_three_in_a_row(self.big_wins, opponent):
            return -10000000 - depth
        if not self.get_valid_moves():
            return 0
        if depth == 0:
            return self.evaluate_position()

        player = self.ai_player if is_maximizing else opponent
        valid_moves = self.order_moves(self.get_valid_moves(), player)

        if is_maximizing:
            max_eval = float("-inf")
            for move in valid_moves:
                undo = self.apply_simulated_move(move, player)
                eval_score = self.minimax(depth - 1, alpha, beta, False)
                self.undo_simulated_move(undo)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval

        min_eval = float("inf")
        for move in valid_moves:
            undo = self.apply_simulated_move(move, player)
            eval_score = self.minimax(depth - 1, alpha, beta, True)
            self.undo_simulated_move(undo)
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

    def apply_simulated_move(self, move, player):
        br, bc, r, c = move
        old_cell = self.boards[br][bc][r][c]
        old_big_win = self.big_wins[br][bc]
        old_next_board = self.next_board

        self.boards[br][bc][r][c] = player
        if old_big_win == EMPTY and self.check_win(self.boards[br][bc]):
            self.big_wins[br][bc] = player
        self.next_board = self.resolve_next_board(r, c)

        return move, old_cell, old_big_win, old_next_board

    def undo_simulated_move(self, undo):
        move, old_cell, old_big_win, old_next_board = undo
        br, bc, r, c = move
        self.boards[br][bc][r][c] = old_cell
        self.big_wins[br][bc] = old_big_win
        self.next_board = old_next_board

    def evaluate_position(self):
        score = 0
        opponent = "X" if self.ai_player == "O" else "O"

        score += self.evaluate_board(self.big_wins, weight=500, strategic=True)

        if self.next_board is None:
            score += 35
        else:
            br, bc = self.next_board
            board_score = self.evaluate_board(self.boards[br][bc], weight=18, strategic=True)
            score += board_score
            if self.player_can_win_board(br, bc, opponent):
                score -= 120
            if self.player_can_win_board(br, bc, self.ai_player):
                score += 90

        for br in range(3):
            for bc in range(3):
                owner = self.big_wins[br][bc]
                if owner == self.ai_player:
                    score += self.square_weight(br, bc) * 30
                elif owner == opponent:
                    score -= self.square_weight(br, bc) * 30
                elif not self.is_full(self.boards[br][bc]):
                    score += self.evaluate_board(
                        self.boards[br][bc],
                        weight=self.square_weight(br, bc),
                        strategic=False,
                    )

        return score

    def square_weight(self, r, c):
        if (r, c) == (1, 1):
            return 6
        if (r, c) in ((0, 0), (0, 2), (2, 0), (2, 2)):
            return 4
        return 3

    def player_can_win_board(self, br, bc, player):
        board = self.boards[br][bc]
        for line in LINES:
            values = [board[r][c] for r, c in line]
            if values.count(player) == 2 and values.count(EMPTY) == 1:
                return True
        return False

    def evaluate_board(self, board, weight=1, strategic=False):
        score = 0
        opponent = "X" if self.ai_player == "O" else "O"

        for line in LINES:
            values = [board[r][c] for r, c in line]
            ai_count = values.count(self.ai_player)
            opponent_count = values.count(opponent)
            empty_count = values.count(EMPTY)
            score += weight * self.score_line(ai_count, opponent_count, empty_count, strategic)

        return score

    def score_line(self, ai_count, opponent_count, empty_count, strategic=False):
        if ai_count and opponent_count:
            return 0
        if ai_count == 3:
            return 2000 if strategic else 200
        if opponent_count == 3:
            return -2000 if strategic else -200
        if ai_count == 2 and empty_count == 1:
            return 260 if strategic else 55
        if opponent_count == 2 and empty_count == 1:
            return -320 if strategic else -70
        if ai_count == 1 and empty_count == 2:
            return 20 if strategic else 8
        if opponent_count == 1 and empty_count == 2:
            return -24 if strategic else -9
        return 0

    def has_three_in_a_row(self, board, player):
        return any(board[a[0]][a[1]] == board[b[0]][b[1]] == board[c[0]][c[1]] == player
                   for a, b, c in LINES)

    def disable_all(self):
        for br in range(3):
            for bc in range(3):
                for r in range(3):
                    for c in range(3):
                        self.buttons[br][bc][r][c].config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    UltimateTicTacToe(root, ai_enabled=True, ai_player="O", search_depth=4)
    root.mainloop()
