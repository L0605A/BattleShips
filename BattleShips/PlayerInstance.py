import tkinter as tk
from tkinter import messagebox


def check_win(board):
    for row in board:
        if any(cell != ' ' and cell != '~' and cell != '*' for cell in row):
            return False
    return True


def get_image(path):
    image = tk.PhotoImage(file=path)
    image = image.zoom(3, 3)
    return image


class PlayerInstance:
    def __init__(self, player_name, game_logic):

        # getting allllll the images needed
        self.rotate_image = get_image("./sprites/RotateButton.png")
        self.button_image = get_image("./sprites/ButtonBackground.png")
        self.water_tile = get_image("./sprites/TileWater.png")
        self.tile = get_image("./sprites/TileBackground.png")
        self.error_tile = get_image("./sprites/TileError.png")
        self.ship_top = get_image("./sprites/ShipTop.png")
        self.ship_bot = get_image("./sprites/ShipBot.png")
        self.ship_col = get_image("./sprites/ShipCol.png")
        self.ship_left = get_image("./sprites/ShipLeft.png")
        self.ship_row = get_image("./sprites/ShipRow.png")
        self.ship_right = get_image("./sprites/ShipRight.png")
        self.ship_one = get_image("./sprites/ShipOne.png")

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
        self.own_buttons = [None for _ in range(10)]
        self.enemy_buttons = [None for _ in range(10)]

        # Make the frame
        self.board_frames = tk.Frame(self.master)

        # Buttons to actually start the game (move to phase 2) for both players
        self.deploy_button1 = tk.Button(self.board_frames, text="Deploy",
                                        font=("Courier New", 10),
                                        command=lambda: self.deploy_ships(),
                                        state='disabled',
                                        borderwidth=0,
                                        image=self.button_image,
                                        compound="center")

        # Rotation buttons
        self.orientation_button = tk.Button(self.board_frames,
                                            borderwidth=0,
                                            command=self.toggle_orientation,
                                            image=self.rotate_image)

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
                    label = tk.Label(self.board_frames, text=chr(64 + col),
                        font=("Courier New", 10), image=self.tile, compound="center")
                    label.grid(row=row, column=col)
                # Make 123 Labels
                elif col == 0 and row > 0:
                    label = tk.Label(self.board_frames, text=row,
                        font=("Courier New", 10), image=self.tile, compound="center")
                    label.grid(row=row, column=col)
                # Make actual clickable buttons for each space
                elif row > 0 and col > 0:
                    button = tk.Button(
                        self.board_frames,
                        text=' ',
                        font=("Courier New", 10),
                        command=lambda r=row - 1, c=col - 1: self.on_button_click(r, c),
                        image=self.water_tile,
                        compound="center",
                        borderwidth=0
                    )
                    button.bind("<Enter>",
                                lambda e, r=row - 1, c=col - 1: self.button_hovered(r, c, True))
                    button.bind("<Leave>",
                                lambda e, r=row - 1, c=col - 1: self.button_hovered(r, c, False))
                    button.grid(row=row, column=col)
                    self.own_buttons[row - 1] = self.own_buttons[row - 1] or []
                    self.own_buttons[row - 1].append(button)

        for i, (ship, size) in enumerate(self.game.ships_info.items()):
            # Buttons for selecting ships
            button1 = tk.Button(
                self.board_frames,
                text=f"{ship} ({size})",
                font=("Courier New", 10),
                command=lambda s=ship, p=1: self.select_ship(s),
                image=self.button_image,
                compound="center",
                borderwidth=0
            )
            button1.grid(row=i+1, column=13)
            self.ship_buttons[(1, ship)] = button1

        # Rotation button
        self.orientation_button.grid(row=len(self.game.ships_info)+3,
                                     column=13)
        # deploy button
        self.deploy_button1.grid(row=len(self.game.ships_info) + 5,
                                 column=13)

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

            for i in range(size):
                image = self.ship_row
                if i == 0: image = self.ship_left
                if i == size-1: image = self.ship_right
                if size == 1: image = self.ship_one
                board[row][col + i] = self.current_ship[0]
                self.own_buttons[row][col + i].config(#text=self.current_ship[0],
                                                  # state='disabled',
                                                  image=image)
        else:
            # If invalid, give em some feedback
            if row + size > 10 or any(board[row + i][col] != ' ' for i in range(size)):
                messagebox.showwarning("Invalid Move", "Cannot place ship here.")
                return

            # If valid, disable the buttons, and populate their board with the ships
            for i in range(size):
                image = self.ship_col
                if i == 0: image = self.ship_top
                if i == size-1: image = self.ship_bot
                if size == 1: image = self.ship_one
                board[row + i][col] = self.current_ship[0]
                self.own_buttons[row + i][col].config(#text=self.current_ship[0],
                                                  # state='disabled',
                                                  image=image)

        # Add a ship to ship tally
        self.deployed_ships[self.current_ship] += 1

        # Disable ship buttons for ships that used up all their ships
        # (and take a shot for each time I said ship in this comment)
        if self.deployed_ships[self.current_ship] == self.ships_amount[self.current_ship]:
            self.ship_buttons[(self.current_turn, self.current_ship)].config(state='disabled')

        # For both players, if all the ships are placed, enable em to press deploy button
        if all(self.deployed_ships[ship] == self.ships_amount[ship] for ship in
               self.deployed_ships):
            self.deploy_button1.config(state='normal')

        # Lastly, reset the ship selection
        self.current_ship = None

    def display_enemy_bard(self):
        # adding enemy board - we will be shooting here!
        for row in range(11):
            for col in range(11):
                # Make ABC labels
                if row == 0 and col > 0:
                    label = tk.Label(self.board_frames, text=chr(64 + col),
                        font=("Courier New", 10), image=self.tile, compound="center")
                    label.grid(row=row, column=col+15)
                # Make 123 Labels
                elif col == 0 and row > 0:
                    label = tk.Label(self.board_frames, text=row,
                        font=("Courier New", 10), image=self.tile, compound="center")
                    label.grid(row=row, column=col+15)
                # Make actual clickable buttons for each space
                elif row > 0 and col > 0:
                    button = tk.Button(
                        self.board_frames,
                        text=' ',
                        font=("Courier New", 10),
                        command=lambda r=row - 1, c=col - 1: self.on_button_click(r, c),
                        image=self.water_tile,
                        compound="center",
                        borderwidth=0
                    )
                    button.grid(row=row, column=col+15)
                    self.enemy_buttons[row - 1] = self.enemy_buttons[row - 1] or []
                    self.enemy_buttons[row - 1].append(button)

    def show_game_boards(self):
        # Enable all buttons
        for player_buttons in self.own_buttons:
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
        self.display_enemy_bard()
        # here should be Supplier loop, so we can get hit/miss and shots info from the other player
        # within here, we access update_enemy_board and receive_shot methods depending on the message received

    def deploy_ships(self):
        self.game.ready_count += 1

        # Disable buttons
        self.deploy_button1.config(state='disabled')
        self.orientation_button.config(state='disabled')

        # here should also disable all buttons from the current player board
        for row in range(10):
            for col in range(10):
                self.own_buttons[row][col].configure(command="None")
        # If player two finished deploying, start the damn thing
        self.game.check_ready()

    def button_hovered(self, row, col, isHovered):
        if isHovered:
            tile_image = self.tile
        else:
            tile_image = self.water_tile
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
                        tile_image = self.error_tile
                    else:
                        tile_image = self.water_tile
                    if col + size > 10:
                        size = 10 - col
                # color the tiles of the ship
                for i in range(size):
                    if board[row][col + i] == ' ':
                        self.own_buttons[row][col + i].configure(image=tile_image)
            # case for vertical placement
            else:
                # if ship is too long or overlays another, display it with a red color, but only when hovering
                if row + size > 10:
                    if isHovered:
                        tile_image = self.error_tile
                    else:
                        tile_image = self.water_tile
                    if row + size > 10:
                        size = 10 - row
                # color the tiles of the ship
                for i in range(size):
                    if board[row + i][col] == ' ':
                        self.own_buttons[row + i][col].configure(image=tile_image)

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

            # process rn: we send a shot, server sends it forward to the second player, 
            # the player responds with hit/miss and updates their board.
            # server then returns the hit/miss to the current player, so he can too 
            # update the board. In the future it should be handled by Kafka
            hit = self.send_shot(row, col)
            self.update_enemy_board(hit, row, col)


            # # Handle misses
            # if board[row][col] == ' ':
            #     board[row][col] = '~'
            #     self.buttons[row][col].config(text='O', bg='red', state='disabled')
            # 
            # # Handle hits
            # else:
            #     board[row][col] = '*'
            #     self.buttons[row][col].config(text='X', bg='green', state='disabled')
            # 
            # # Handle wins
            # if check_win(board):
            #     messagebox.showinfo("Game Over", f"Player {self.player_name} wins!")
            #     self.master.quit()
            # else:
            #     self.game.next_turn()

    def send_shot(self, row, col):
        # here will be the Kafka Supplier Code
        # for now, sending to server instead
        return self.game.receive(self, row, col, "fire")

    def receive_shot(self, row, col):
        # disabling the tile, so we know where enemy has already shot
        self.own_buttons[row][col].config(state='disabled')
        # here checking if were hit
        # should be sending info via Kafka instead
        return self.player_board[row][col] != ' '
    def update_enemy_board(self, hit, row, col):
        if hit:
            self.enemy_buttons[row][col].config(image=self.error_tile)
        else:
            self.enemy_buttons[row][col].config(image=self.tile)
