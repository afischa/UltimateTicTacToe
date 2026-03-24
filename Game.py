import tkinter as tk

class UltimateTicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Tic Tac Toe")

        self.current_player = "X"
        self.next_board = None  # (row, col)

        self.boards = [[[[ "" for _ in range(3)] for _ in range(3)]
                        for _ in range(3)] for _ in range(3)]

        self.big_wins = [["" for _ in range(3)] for _ in range(3)]

        self.buttons = [[[[None for _ in range(3)] for _ in range(3)]
                         for _ in range(3)] for _ in range(3)]

        self.status = tk.Label(root, text="Player X's turn", font=("Arial", 16))
        self.status.grid(row=0, column=0, columnspan=9)

        self.create_board()
        self.highlight_active_board()

    def create_board(self):
        for big_r in range(3):
            for big_c in range(3):
                frame = tk.Frame(self.root, bd=3, relief="solid")
                frame.grid(row=big_r + 1, column=big_c, padx=3, pady=3)

                for r in range(3):
                    for c in range(3):
                        btn = tk.Button(
                            frame,
                            text="",
                            width=4,
                            height=2,
                            font=("Arial", 14),
                            bg="white",
                            command=lambda br=big_r, bc=big_c, r=r, c=c:
                                self.make_move(br, bc, r, c)
                        )
                        btn.grid(row=r, column=c)
                        self.buttons[big_r][big_c][r][c] = btn

    def make_move(self, br, bc, r, c):
        if self.boards[br][bc][r][c] != "":
            return

        if self.big_wins[br][bc] != "":
            return

        if self.next_board is not None and (br, bc) != self.next_board:
            return

        self.boards[br][bc][r][c] = self.current_player

        btn = self.buttons[br][bc][r][c]
        btn.config(text=self.current_player, bg="white")

        # check local win
        if self.check_win(self.boards[br][bc]):
            self.big_wins[br][bc] = self.current_player
            self.color_won_board(br, bc, self.current_player)

        # check global win
        if self.check_win(self.big_wins):
            self.status.config(text=f"Player {self.current_player} wins!")
            self.disable_all()
            return

        # next board logic
        self.next_board = (r, c)
        if (
            self.big_wins[r][c] != "" or
            self.is_full(self.boards[r][c])
        ):
            self.next_board = None

        # switch player
        self.current_player = "O" if self.current_player == "X" else "X"

        self.update_status()
        self.highlight_active_board()

    #X win = red, O win = blue
    def color_won_board(self, br, bc, player):
        color = "red" if player == "X" else "lightblue"

        for r in range(3):
            for c in range(3):
                self.buttons[br][bc][r][c].config(bg=color)

    def highlight_active_board(self):
        for br in range(3):
            for bc in range(3):
                for r in range(3):
                    for c in range(3):
                        btn = self.buttons[br][bc][r][c]

                        # keep won boards colored
                        if self.big_wins[br][bc] != "":
                            continue

                        # keep played cells unchanged
                        if self.boards[br][bc][r][c] != "":
                            continue

                        if self.next_board is None:
                            btn.config(bg="white")
                        elif (br, bc) == self.next_board:
                            btn.config(bg="lightyellow")
                        else:
                            btn.config(bg="#dddddd")

    def update_status(self):
        if self.next_board:
            self.status.config(
                text=f"Player {self.current_player}'s turn (Board {self.next_board})"
            )
        else:
            self.status.config(
                text=f"Player {self.current_player}'s turn (Anywhere valid board)"
            )

    def check_win(self, board):
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != "":
                return True
            if board[0][i] == board[1][i] == board[2][i] != "":
                return True

        if board[0][0] == board[1][1] == board[2][2] != "":
            return True
        if board[0][2] == board[1][1] == board[2][0] != "":
            return True

        return False

    def is_full(self, board):
        return all(cell != "" for row in board for cell in row)

    def disable_all(self):
        for br in range(3):
            for bc in range(3):
                for r in range(3):
                    for c in range(3):
                        self.buttons[br][bc][r][c].config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    game = UltimateTicTacToe(root)
    root.mainloop()