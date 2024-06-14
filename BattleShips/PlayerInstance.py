import tkinter as tk
from tkinter import messagebox


def check_win(board):
    for row in board:
        if any(cell != ' ' and cell != '~' and cell != '*' for cell in row):
            return False
    return True


class PlayerInstance:
    def __init__(self, player_name, game_logic):
        self.current_turn = True
        self.game = game_logic
        self.player_name = player_name
        self.master = tk.Toplevel(game_logic.master)

        # Show window name
        self.master.title("Battleships: " + player_name)

        # Initialise boards
        self.player_board = [[' '] * 10 for _ in range(10)]

        # Here be amounts of ships
        self.ships_amount = self.game.ships_amount

        # Initialised deployed ships
        self.deployed_ships = {ship: 0 for ship in self.game.ships_info}

        # Default values for ship deployment
        self.current_ship = None
        self.ship_orientation = 'H'

        # Buttons for ship selection
        self.ship_buttons = {}

        # Make buttons for each space - tiles on a display board
        self.buttons = [None for _ in range(10)]

        # Make the frame
        self.board_frames = tk.Frame(self.master)

        # Buttons to actually start the game (move to phase 2) for both players
        self.deploy_button1 = tk.Button(self.board_frames, text="Deploy", command=lambda: self.deploy_ships(),
                                        state='disabled')

        # Rotation buttons
        self.orientation_button = tk.Button(self.board_frames, text="Rotate (H)", command=self.toggle_orientation)

        self.create_deploy_screen()

    # letting server know that the player has finished deployment phase
    def confirm(self):
        if self.player_name == "Player 1":
            self.game.player1_ready.set()
        elif self.player_name == "Player 2":
            self.game.player2_ready.set()

    def create_deploy_screen(self):
        # Make the frame
        self.board_frames.grid(row=13, column=13)

        # Make buttons for each space - tiles on a board
        for row in range(11):
            for col in range(11):
                # Make ABC labels
                if row == 0 and col > 0:
                    label = tk.Label(self.board_frames, text=chr(64 + col), width=4, height=2)
                    label.grid(row=row, column=col)
                # Make 123 Labels
                elif col == 0 and row > 0:
                    label = tk.Label(self.board_frames, text=row, width=4, height=2)
                    label.grid(row=row, column=col)
                # Make actual clickable buttons for each space
                elif row > 0 and col > 0:
                    button = tk.Button(
                        self.board_frames,
                        text=' ',
                        width=4,
                        height=2,
                        command=lambda r=row - 1, c=col - 1: self.on_button_click(r, c)
                    )
                    button.bind("<Enter>",
                                lambda e, r=row - 1, c=col - 1: self.button_hovered(r, c, True))
                    button.bind("<Leave>",
                                lambda e, r=row - 1, c=col - 1: self.button_hovered(r, c, False))
                    button.grid(row=row, column=col)
                    self.buttons[row - 1] = self.buttons[row - 1] or []
                    self.buttons[row - 1].append(button)

        for i, (ship, size) in enumerate(self.game.ships_info.items()):
            # Buttons for player one
            button1 = tk.Button(
                self.board_frames,
                text=f"{ship} ({size})",
                command=lambda s=ship, p=1: self.select_ship(s)
            )
            button1.grid(row=i+1, column=13)
            self.ship_buttons[(1, ship)] = button1

        # Rotation buttons
        self.orientation_button.grid(row=len(self.game.ships_info)+3, column=13)

        self.deploy_button1.grid(row=len(self.game.ships_info) + 5, column=13)

    def select_ship(self, ship):
        self.current_ship = ship

    def toggle_orientation(self):
        # Indicate current ship orientation
        self.ship_orientation = 'H' if self.ship_orientation == 'V' else 'V'
        self.orientation_button.config(text=f"Rotate ({self.ship_orientation})")

    def place_ship(self, row, col):

        # Show the player a warning if they didn't select a ship yet
        if not self.current_ship:
            messagebox.showwarning("Invalid Move", "Please select a ship to place.")
            return

        # Get the size of the ship that's gon be placed
        size = self.game.ships_info[self.current_ship]

        # Get the board it's gon be placed on //always THIS player duh
        board = self.player_board

        # Check for placement validity: both vertical, and horizontal
        if self.ship_orientation == 'H':
            # If invalid, give em some feedback
            if col + size > 10 or any(board[row][col + i] != ' ' for i in range(size)):
                messagebox.showwarning("Invalid Move", "Cannot place ship here.")
                return

            # If valid, disable the buttons, and populate their board with the ships
            # !!!!!!!!!
            for i in range(size):
                board[row][col + i] = self.current_ship[0]
                self.buttons[row][col + i].config(text=self.current_ship[0], state='disabled')
        else:
            # If invalid, give em some feedback
            if row + size > 10 or any(board[row + i][col] != ' ' for i in range(size)):
                messagebox.showwarning("Invalid Move", "Cannot place ship here.")
                return

            # If valid, disable the buttons, and populate their board with the ships
            for i in range(size):
                board[row + i][col] = self.current_ship[0]
                self.buttons[row + i][col].config(text=self.current_ship[0], state='disabled')

        # Add a ship to ship tally
        self.deployed_ships[self.current_ship] += 1

        # Disable ship buttons for ships that used up all their ships
        # (and take a shot for each time I said ship in this comment)
        if self.deployed_ships[self.current_ship] == self.ships_amount[self.current_ship]:
            self.ship_buttons[(self.current_turn, self.current_ship)].config(state='disabled')

        # For both players, if all the ships are placed, enable em to press deploy button
        if all(self.deployed_ships[ship] == self.ships_amount[ship] for ship in
               self.deployed_ships):
            if self.current_turn == 1:
                self.deploy_button1.config(state='normal')

        # Lastly, reset the ship selection
        self.current_ship = None

    def create_game_board(self):
        # adding enemy board - we will be shooting here!
        for row in range(11):
            for col in range(11):
                # Make ABC labels
                if row == 0 and col > 0:
                    label = tk.Label(self.board_frames, text=chr(64 + col), width=4, height=2)
                    label.grid(row=row, column=col+15)
                # Make 123 Labels
                elif col == 0 and row > 0:
                    label = tk.Label(self.board_frames, text=row, width=4, height=2)
                    label.grid(row=row, column=col+15)
                # Make actual clickable buttons for each space
                elif row > 0 and col > 0:
                    button = tk.Button(
                        self.board_frames,
                        text=' ',
                        width=4,
                        height=2,
                        state=tk.NORMAL,
                        command=lambda r=row - 1, c=col - 1: self.on_button_click(r, c)
                    )
                    button.grid(row=row, column=col+15)

    def show_game_boards(self):
        # Enable all buttons
        for player_buttons in self.buttons:
            for button in player_buttons:
                button.config(state='normal')

        for _, button in self.ship_buttons.items():
            button.grid_remove()
        self.orientation_button.grid_remove()

        # Remove deployment buttons
        self.deploy_button1.grid_remove()

        # Remove ships from boards
        for row in self.board_frames:
            for widget in row.winfo_children():
                if widget.winfo_class() != "Label":
                    widget.config(text='')

    def start_game(self):
        print("starting the game for " + self.player_name)
        self.create_game_board()

    def deploy_ships(self):
        self.game.ready_count += 1

        # If player one finished deploying their ships, move to player two
        self.deploy_button1.config(state='disabled')

        # If player two finished deploying, start the damn thing
        self.game.check_ready()

    def button_hovered(self, row, col, isHovered):
        if isHovered:
            empty_color = "gray"
            ship_color = "red"
        else:
            empty_color = "white"
            ship_color = "gray"
        # get current player board
        board = self.player_board

        # working only if player selected a ship to place
        if self.current_ship is not None:
            # Get the size of the ship that's gon be placed
            size = self.game.ships_info[self.current_ship]
            # case for horizontal placement
            if self.ship_orientation == "H":
                # if ship is too long or overlays another, display it with a red color, but only when hovering
                if col + size > 10:
                    if isHovered:
                        empty_color = "red"
                    else:
                        empty_color = "white"
                    if col + size > 10:
                        size = 10 - col
                # color the tiles of the ship
                for i in range(size):
                    if board[row][col + i] != ' ':
                        self.buttons[row][col + i].configure(bg=ship_color)
                    else:
                        self.buttons[row][col + i].configure(bg=empty_color)
            # case for vertical placement
            else:
                # if ship is too long or overlays another, display it with a red color, but only when hovering
                if row + size > 10:
                    if isHovered:
                        empty_color = "red"
                    else:
                        empty_color = "white"
                    if row + size > 10:
                        size = 10 - row
                # color the tiles of the ship
                for i in range(size):
                    if board[row + i][col] != ' ':
                        self.buttons[row + i][col].configure(bg=ship_color)
                    else:
                        self.buttons[row + i][col].configure(bg=empty_color)

    def on_button_click(self, row, col):

        # If in deployment phase, deploy the boy
        if self.game.phase == 1:
            self.place_ship(row, col)

        # If in action phase, fire a shot
        elif self.game.phase == 2:
            if not self.current_turn:
                messagebox.showwarning("Invalid Move", "It's not your turn!")
                return

            board = self.player_board

            # Handle misses
            if board[row][col] == ' ':
                board[row][col] = '~'
                self.buttons[row][col].config(text='O', bg='red', state='disabled')

            # Handle hits
            else:
                board[row][col] = '*'
                self.buttons[row][col].config(text='X', bg='green', state='disabled')

            # Handle wins
            if check_win(board):
                messagebox.showinfo("Game Over", f"Player {self.player_name} wins!")
                self.master.quit()
            else:
                self.game.next_turn()
