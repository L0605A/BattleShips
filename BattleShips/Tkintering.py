import tkinter as tk
from tkinter import messagebox


class Tinktering:
    def __init__(self, master):

        self.master = master

        # Show window name
        self.master.title("Battleships")

        # Here be ship sizes
        self.ships_info = {
            "Carrier": 5,
            "Battleship": 4,
            "Cruiser": 3,
            "Submarine": 2,
            "Destroyer": 1
        }

        # Here be amounts of ships
        self.ships_amount = {
            "Carrier": 1,
            "Battleship": 1,
            "Cruiser": 1,
            "Submarine": 1,
            "Destroyer": 1
        }

        # Initialise boards
        self.player1_board = [[' '] * 10 for _ in range(10)]
        self.player2_board = [[' '] * 10 for _ in range(10)]

        # Initialised deployed ships
        self.deployed_ships = {1: {ship: 0 for ship in self.ships_info}, 2: {ship: 0 for ship in self.ships_info}}

        # Start on player 1
        self.current_turn = 1

        # Phase 1 = Deployment, Phase 2 = Actual Game
        self.phase = 1

        # Default values for ship deployment
        self.current_ship = None
        self.ship_orientation = 'H'

        # Run GUI creation
        self.create_widgets()

    def create_widgets(self):

        # Make the frame
        self.board_frames = [tk.Frame(self.master) for _ in range(2)]
        for i, frame in enumerate(self.board_frames):
            frame.grid(row=0, column=2 * i + 1)

        # Make buttons for each space
        self.buttons = [[None for _ in range(10)] for _ in range(2)]
        for player in range(2):
            for row in range(11):
                for col in range(11):
                    # Make ABC labels
                    if row == 0 and col > 0:
                        label = tk.Label(self.board_frames[player], text=chr(64 + col), width=4, height=2)
                        label.grid(row=row, column=col)
                    # Make 123 Labels
                    elif col == 0 and row > 0:
                        label = tk.Label(self.board_frames[player], text=row, width=4, height=2)
                        label.grid(row=row, column=col)
                    # Make actual clickable buttons for each space
                    elif row > 0 and col > 0:
                        button = tk.Button(
                            self.board_frames[player],
                            text=' ',
                            width=4,
                            height=2,
                            command=lambda r=row - 1, c=col - 1, p=player: self.on_button_click(r, c, p)
                        )
                        button.bind("<Enter>",
                                    lambda e, r=row - 1, c=col - 1, p=player: self.button_hovered(r, c, p, True))
                        button.bind("<Leave>",
                                    lambda e, r=row - 1, c=col - 1, p=player: self.button_hovered(r, c, p, False))
                        button.grid(row=row, column=col)
                        self.buttons[player][row - 1] = self.buttons[player][row - 1] or []
                        self.buttons[player][row - 1].append(button)

        # Buttons for ship selection
        self.ship_buttons = {}

        for i, (ship, size) in enumerate(self.ships_info.items()):
            # Buttons for plater one
            button1 = tk.Button(
                self.master,
                text=f"{ship} ({size})",
                command=lambda s=ship, p=1: self.select_ship(s, p)
            )
            button1.grid(row=i, column=0)
            self.ship_buttons[(1, ship)] = button1

            # Buttons for player two
            button2 = tk.Button(
                self.master,
                text=f"{ship} ({size})",
                command=lambda s=ship, p=2: self.select_ship(s, p)
            )
            button2.grid(row=i, column=4)
            self.ship_buttons[(2, ship)] = button2

        # Rotation buttons
        self.orientation_button = tk.Button(self.master, text="Rotate (H)", command=self.toggle_orientation)
        self.orientation_button.grid(row=len(self.ships_info), column=0)

        # Buttons to actually start the game (move to phase 2) for both players
        self.deploy_button1 = tk.Button(self.master, text="Deploy", command=lambda: self.deploy_ships(1),
                                        state='disabled')
        self.deploy_button1.grid(row=len(self.ships_info) + 1, column=1)

        self.deploy_button2 = tk.Button(self.master, text="Deploy", command=lambda: self.deploy_ships(2),
                                        state='disabled')
        self.deploy_button2.grid(row=len(self.ships_info) + 1, column=3)

    def select_ship(self, ship, player):
        if self.current_turn != player:
            messagebox.showwarning("Invalid Move", "It's not your turn!")
            return
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
        size = self.ships_info[self.current_ship]

        # Get the board it's gon be placed on
        board = self.player1_board if self.current_turn == 1 else self.player2_board

        # Check for placement validity: both vertical, and horizontal
        if self.ship_orientation == 'H':
            # If invalid, give em some feedback
            if col + size > 10 or any(board[row][col + i] != ' ' for i in range(size)):
                messagebox.showwarning("Invalid Move", "Cannot place ship here.")
                return

            # If valid, disable the buttons, and populate their board with the ships
            for i in range(size):
                board[row][col + i] = self.current_ship[0]
                self.buttons[self.current_turn - 1][row][col + i].config(text=self.current_ship[0], state='disabled')
        else:
            # If invalid, give em some feedback
            if row + size > 10 or any(board[row + i][col] != ' ' for i in range(size)):
                messagebox.showwarning("Invalid Move", "Cannot place ship here.")
                return

            # If valid, disable the buttons, and populate their board with the ships
            for i in range(size):
                board[row + i][col] = self.current_ship[0]
                self.buttons[self.current_turn - 1][row + i][col].config(text=self.current_ship[0], state='disabled')

        # Add a ship to ship tally
        self.deployed_ships[self.current_turn][self.current_ship] += 1

        # Disable ship buttons for ships that used up all their ships
        # (and take a shot for each time I said ship in this comment)
        if self.deployed_ships[self.current_turn][self.current_ship] == self.ships_amount[self.current_ship]:
            self.ship_buttons[(self.current_turn, self.current_ship)].config(state='disabled')

        # For both players, if all the ships are placed, enable em to press deploy button
        if all(self.deployed_ships[self.current_turn][ship] == self.ships_amount[ship] for ship in
               self.deployed_ships[self.current_turn]):
            if self.current_turn == 1:
                self.deploy_button1.config(state='normal')
            else:
                self.deploy_button2.config(state='normal')

        # Lastly, reset the ship selection
        self.current_ship = None

    def show_game_boards(self):

        # Enable all buttons
        for player_buttons in self.buttons:
            for row_buttons in player_buttons:
                for button in row_buttons:
                    button.config(state='normal')

        for _, button in self.ship_buttons.items():
            button.grid_remove()
        self.orientation_button.grid_remove()

        # Remove deployment buttons
        self.deploy_button1.grid_remove()
        self.deploy_button2.grid_remove()

        # Remove ships from boars
        for row in self.board_frames:
            for widget in row.winfo_children():
                if widget.winfo_class() != "Label":
                    widget.config(text='')

    def deploy_ships(self, player):

        # If player one finished deploying their ships, move to player two
        if player == 1:
            self.deploy_button1.config(state='disabled')
            self.current_turn = 2
        # If player two finished deploying, start the damn thing
        else:
            self.deploy_button2.config(state='disabled')
            if all(self.deployed_ships[1][ship] == self.ships_amount[ship] for ship in self.ships_info) and all(
                    self.deployed_ships[2][ship] == self.ships_amount[ship] for ship in self.ships_info):
                # Move to the actual game
                self.phase = 2

                # Reset turns: player 1 should start
                self.current_turn = 1

                # Prepare the boards in all their glory
                self.show_game_boards()

    def button_hovered(self, row, col, player, isHovered):
        if isHovered:
            empty_color = "gray"
            ship_color = "red"
        else:
            empty_color = "white"
            ship_color = "gray"
        # get current player board
        board = self.player1_board if player == 0 else self.player2_board

        # working only if player selected a ship to place
        if self.current_ship is not None:
            # Get the size of the ship that's gon be placed
            size = self.ships_info[self.current_ship]
            # case for horizontal placement
            if self.ship_orientation == "H":
                # if ship is too long or overlays another, display it with a red color, but only when hovering
                if col + size > 10:
                    if isHovered:
                        empty_color = "red"
                    else:
                        empty_color = "white"
                    if col + size > 10:
                        size = 10-col
                # color the tiles of the ship
                for i in range(size):
                    if board[row][col+i] != ' ':
                        self.buttons[player][row][col+i].configure(bg=ship_color)
                    else:
                        self.buttons[player][row][col+i].configure(bg=empty_color)
            # case for vertical placement
            else:
                # if ship is too long or overlays another, display it with a red color, but only when hovering
                if row + size > 10:
                    if isHovered:
                        empty_color = "red"
                    else:
                        empty_color = "white"
                    if row + size > 10:
                        size = 10-row
                # color the tiles of the ship
                for i in range(size):
                    if board[row+i][col] != ' ':
                        self.buttons[player][row+i][col].configure(bg=ship_color)
                    else:
                        self.buttons[player][row+i][col].configure(bg=empty_color)

    def on_button_click(self, row, col, player):

        # If in deployment phase, deploy the boy
        if self.phase == 1:
            if self.current_turn == player + 1:
                self.place_ship(row, col)
            else:
                messagebox.showwarning("Invalid Move", "It's not your turn!")

        # If in action phase, fire a shot
        elif self.phase == 2:
            if self.current_turn == 1 and player == 1 or self.current_turn == 2 and player == 0:
                messagebox.showwarning("Invalid Move", "It's not your turn!")
                return

            board = self.player2_board if player == 0 else self.player1_board

            # Handle misses
            if board[row][col] == ' ':
                board[row][col] = '~'
                self.buttons[player][row][col].config(text='O', bg='red', state='disabled')

            # Handle hits
            else:
                board[row][col] = '*'
                self.buttons[player][row][col].config(text='X', bg='green', state='disabled')

            # Handle wins
            if self.check_win(board):
                messagebox.showinfo("Game Over", f"Player {self.current_turn} wins!")
                self.master.quit()
            else:
                self.current_turn = 2 if self.current_turn == 1 else 1

    def check_win(self, board):
        for row in board:
            if any(cell != ' ' and cell != '~' and cell != '*' for cell in row):
                return False
        return True


if __name__ == "__main__":
    root = tk.Tk()
    game = Tinktering(root)
    root.mainloop()


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
                        self.own_buttons[row][col + i].configure(bg=ship_color)
                    else:
                        self.own_buttons[row][col + i].configure(bg=empty_color)
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
                        self.own_buttons[row + i][col].configure(bg=ship_color)
                    else:
                        self.own_buttons[row + i][col].configure(bg=empty_color)