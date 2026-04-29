import tkinter as tk
from copy import deepcopy

class UltimateTicTacToe:
    def __init__(self, root, ai_enabled=True, ai_player="O", search_depth=4):
        self.root = root
        self.root.title("Ultimate Tic Tac Toe - AI Enabled")

        self.current_player = "X"
        self.next_board = None  # (row, col)
        
        # AI settings
        self.ai_enabled = ai_enabled
        self.ai_player = ai_player
        self.search_depth = search_depth
        self.ai_thinking = False

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

    def make_move(self, br, bc, r, c, is_ai_move=False):
        # Block player moves during AI thinking (but allow AI to make its move)
        if self.ai_thinking and not is_ai_move:
            return
            
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
        
        # AI turn
        if self.ai_enabled and self.current_player == self.ai_player and not is_ai_move:
            self.root.after(500, self.ai_move)

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

    def ai_move(self):
        """AI makes the best move using minimax with alpha-beta pruning"""
        self.ai_thinking = True
        self.status.config(text=f"AI ({self.ai_player}) is thinking...")
        self.root.update()
        
        best_move = None
        best_score = float('-inf')
        
        # Get valid moves
        valid_moves = self.get_valid_moves()
        
        if not valid_moves:
            self.status.config(text="Game is a draw!")
            self.ai_thinking = False
            return
        
        # Order moves - prioritize winning, blocking, and strategic moves
        ordered_moves = self.order_moves(valid_moves)
        
        # Find best move using minimax
        for move in ordered_moves:
            br, bc, r, c = move
            
            # Make temporary move
            self.boards[br][bc][r][c] = self.ai_player
            
            # Update board state for proper evaluation
            old_big_wins = self.big_wins[br][bc]
            if self.check_win(self.boards[br][bc]):
                self.big_wins[br][bc] = self.ai_player
            
            old_next_board = self.next_board
            new_next_board = (r, c)
            if self.big_wins[r][c] != "" or self.is_full(self.boards[r][c]):
                new_next_board = None
            self.next_board = new_next_board
            
            # Evaluate position
            score = self.minimax(self.search_depth - 1, float('-inf'), float('inf'), False)
            
            # Undo temporary move and restore state
            self.boards[br][bc][r][c] = ""
            self.big_wins[br][bc] = old_big_wins
            self.next_board = old_next_board
            
            if score > best_score:
                best_score = score
                best_move = move
        
        self.ai_thinking = False
        
        if best_move:
            br, bc, r, c = best_move
            self.make_move(br, bc, r, c, is_ai_move=True)
    
    def order_moves(self, moves):
        """Order moves to improve alpha-beta pruning efficiency"""
        opponent = "X" if self.ai_player == "O" else "O"
        move_scores = []
        
        for move in moves:
            br, bc, r, c = move
            score = 0
            
            # Check if this move wins the game
            test_board = [row[:] for row in self.boards[br][bc]]
            test_board[r][c] = self.ai_player
            if self.check_win(test_board):
                if self.check_win(self.big_wins):  # Would win global board
                    score += 10000
                else:
                    score += 100
            
            # Check if this move blocks opponent from winning
            test_board = [row[:] for row in self.boards[br][bc]]
            test_board[r][c] = opponent
            if self.check_win(test_board):
                score += 50
            
            # Prioritize center boards
            if br == 1 and bc == 1:
                score += 10
            elif (br, bc) != self.next_board and self.next_board is not None:
                score -= 5  # Deprioritize moves that lead to filled boards
            
            move_scores.append((score, move))
        
        # Sort by score descending
        move_scores.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in move_scores]
    
    def get_valid_moves(self):
        """Get all valid moves for current board state"""
        valid_moves = []
        
        if self.next_board is None:
            # Can play anywhere
            for br in range(3):
                for bc in range(3):
                    if self.big_wins[br][bc] == "" and not self.is_full(self.boards[br][bc]):
                        for r in range(3):
                            for c in range(3):
                                if self.boards[br][bc][r][c] == "":
                                    valid_moves.append((br, bc, r, c))
        else:
            # Must play in next_board
            br, bc = self.next_board
            if self.big_wins[br][bc] == "":
                for r in range(3):
                    for c in range(3):
                        if self.boards[br][bc][r][c] == "":
                            valid_moves.append((br, bc, r, c))
        
        return valid_moves
    
    def minimax(self, depth, alpha, beta, is_maximizing):
        """
        Minimax algorithm with alpha-beta pruning.
        is_maximizing: True when AI player is maximizing, False when opponent is minimizing
        """
        # Terminal states - check for wins
        opponent = "X" if self.ai_player == "O" else "O"
        
        # Check for AI win
        if self.has_three_in_a_row(self.big_wins, self.ai_player):
            return 1000 + depth
        
        # Check for opponent win
        if self.has_three_in_a_row(self.big_wins, opponent):
            return -1000 - depth
        
        # Check for draw
        if self.is_game_full():
            return 0
        
        # Depth limit reached - use heuristic evaluation
        if depth == 0:
            return self.evaluate_position()
        
        valid_moves = self.get_valid_moves()
        
        if not valid_moves:
            return 0
        
        if is_maximizing:
            # AI player's turn (maximize)
            max_eval = float('-inf')
            
            for move in valid_moves:
                br, bc, r, c = move
                
                # Make move
                self.boards[br][bc][r][c] = self.ai_player
                
                # Track if this completes a board
                old_big_wins = self.big_wins[br][bc]
                if self.check_win(self.boards[br][bc]):
                    self.big_wins[br][bc] = self.ai_player
                
                # Calculate next board after this move
                old_next_board = self.next_board
                new_next_board = (r, c)
                if self.big_wins[r][c] != "" or self.is_full(self.boards[r][c]):
                    new_next_board = None
                self.next_board = new_next_board
                
                # Recursive call
                eval_score = self.minimax(depth - 1, alpha, beta, False)
                
                # Undo move
                self.boards[br][bc][r][c] = ""
                self.big_wins[br][bc] = old_big_wins
                self.next_board = old_next_board
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_eval
        else:
            # Opponent's turn (minimize)
            min_eval = float('inf')
            
            for move in valid_moves:
                br, bc, r, c = move
                
                # Make move
                self.boards[br][bc][r][c] = opponent
                
                # Track if this completes a board
                old_big_wins = self.big_wins[br][bc]
                if self.check_win(self.boards[br][bc]):
                    self.big_wins[br][bc] = opponent
                
                # Calculate next board after this move
                old_next_board = self.next_board
                new_next_board = (r, c)
                if self.big_wins[r][c] != "" or self.is_full(self.boards[r][c]):
                    new_next_board = None
                self.next_board = new_next_board
                
                # Recursive call
                eval_score = self.minimax(depth - 1, alpha, beta, True)
                
                # Undo move
                self.boards[br][bc][r][c] = ""
                self.big_wins[br][bc] = old_big_wins
                self.next_board = old_next_board
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_eval
    
    def evaluate_position(self):
        """
        Heuristic evaluation function for board position.
        Returns a score indicating how good the position is for the AI.
        """
        score = 0
        opponent = "X" if self.ai_player == "O" else "O"
        
        # Heavily weight the global board (big_wins) - this is what matters most
        score += self.evaluate_board(self.big_wins, weight=100, strategic=True)
        
        # Evaluate where opponent is forced to play
        if self.next_board is not None:
            br, bc = self.next_board
            if self.big_wins[br][bc] == "":
                # Opponent is forced into this board - weight it heavily
                score += self.evaluate_board(self.boards[br][bc], weight=10, strategic=True)
            # If opponent is forced into a won board, they get free play (bad for AI)
        
        # Evaluate individual boards based on their strategic importance
        for board_r in range(3):
            for board_c in range(3):
                if self.big_wins[board_r][board_c] == "":
                    if (board_r, board_c) == self.next_board:
                        continue  # Already evaluated above
                    
                    # Strategic boards: corners, edges, center
                    if board_r == 1 and board_c == 1:  # Center board
                        weight = 8
                    elif (board_r == 0 and board_c == 0) or (board_r == 0 and board_c == 2) or (board_r == 2 and board_c == 0) or (board_r == 2 and board_c == 2):
                        weight = 2  # Corner boards
                    else:
                        weight = 3  # Edge boards
                    
                    score += self.evaluate_board(self.boards[board_r][board_c], weight=weight, strategic=False)
        
        # Bonus for controlling the center position (3x3 center of the big board)
        score += self.center_control_bonus()
        
        return score
    
    def center_control_bonus(self):
        """Bonus for controlling center cells of each board"""
        opponent = "X" if self.ai_player == "O" else "O"
        bonus = 0
        
        # Check center of big board
        for br in range(3):
            for bc in range(3):
                if self.big_wins[br][bc] == self.ai_player:
                    bonus += 20
                elif self.big_wins[br][bc] == opponent:
                    bonus -= 20
        
        return bonus
    
    def evaluate_board(self, board, weight=1, strategic=False):
        """Evaluate a single 3x3 board"""
        score = 0
        opponent = "X" if self.ai_player == "O" else "O"
        
        # Check rows
        for i in range(3):
            ai_count = sum(1 for j in range(3) if board[i][j] == self.ai_player)
            opponent_count = sum(1 for j in range(3) if board[i][j] == opponent)
            empty_count = sum(1 for j in range(3) if board[i][j] == "")
            
            score += weight * self.score_line(ai_count, opponent_count, empty_count, strategic)
        
        # Check columns
        for j in range(3):
            ai_count = sum(1 for i in range(3) if board[i][j] == self.ai_player)
            opponent_count = sum(1 for i in range(3) if board[i][j] == opponent)
            empty_count = sum(1 for i in range(3) if board[i][j] == "")
            
            score += weight * self.score_line(ai_count, opponent_count, empty_count, strategic)
        
        # Check diagonals
        ai_count = sum(1 for i in range(3) if board[i][i] == self.ai_player)
        opponent_count = sum(1 for i in range(3) if board[i][i] == opponent)
        empty_count = sum(1 for i in range(3) if board[i][i] == "")
        score += weight * self.score_line(ai_count, opponent_count, empty_count, strategic)
        
        ai_count = sum(1 for i in range(3) if board[i][2-i] == self.ai_player)
        opponent_count = sum(1 for i in range(3) if board[i][2-i] == opponent)
        empty_count = sum(1 for i in range(3) if board[i][2-i] == "")
        score += weight * self.score_line(ai_count, opponent_count, empty_count, strategic)
        
        return score
    
    def score_line(self, ai_count, opponent_count, empty_count, strategic=False):
        """Score a line (row, column, or diagonal)"""
        # Winning line
        if ai_count == 3:
            return 1000 if strategic else 100
        if opponent_count == 3:
            return -1000 if strategic else -100
        
        # Two AI, one empty (setup for winning) - VERY HIGH priority
        if ai_count == 2 and empty_count == 1:
            return 200 if strategic else 50
        
        # Two opponent, one empty (blocking opponent) - HIGH priority
        if opponent_count == 2 and empty_count == 1:
            return -200 if strategic else -50
        
        # One AI, one opponent - blocked line
        if ai_count == 1 and opponent_count == 1:
            return -5 if strategic else -2
        
        # One AI, two empty (potential)
        if ai_count == 1 and empty_count == 2:
            return 8 if strategic else 2
        
        # One opponent, two empty
        if opponent_count == 1 and empty_count == 2:
            return -8 if strategic else -2
        
        return 0
    
    def has_three_in_a_row(self, board, player):
        """Check if a player has three in a row anywhere on the board"""
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] == player:
                return True
            if board[0][i] == board[1][i] == board[2][i] == player:
                return True
        
        if board[0][0] == board[1][1] == board[2][2] == player:
            return True
        if board[0][2] == board[1][1] == board[2][0] == player:
            return True
        
        return False
    
    def is_game_full(self):
        """Check if all boards are filled"""
        return all(self.is_full(self.boards[br][bc]) 
                   for br in range(3) for bc in range(3))

    def disable_all(self):
        for br in range(3):
            for bc in range(3):
                for r in range(3):
                    for c in range(3):
                        self.buttons[br][bc][r][c].config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    # Create game with AI enabled (AI plays as O, searches 6 moves ahead with move ordering)
    game = UltimateTicTacToe(root, ai_enabled=True, ai_player="O", search_depth=6)
    root.mainloop()