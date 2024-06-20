import tkinter as tk
import KafkaTesting as kafka
import PlayerInstance as client


class GameLogic:
    def __init__(self):
        self.master = tk.Tk()

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

        self.ready_count = 0

        # Initialised deployed ships
        self.deployed_ships = {1: {ship: 0 for ship in self.ships_info}, 2: {ship: 0 for ship in self.ships_info}}

        # Start on player 1
        self.current_turn = 1

        # Phase 1 = Deployment, Phase 2 = Actual Game
        self.phase = 1

        # init players
        self.player1 = client.PlayerInstance("Player 1", self)
        self.player2 = client.PlayerInstance("Player 2", self)

        image = tk.PhotoImage(file="./sprites/TileWater.png")
        image = image.zoom(3, 3)
        img = tk.Label(self.master, image=image)
        # img.pack()

        self.master.mainloop()

    def check_ready(self):
        if self.ready_count == 2:
            self.start_game()

    def next_turn(self):
        if self.current_turn == 1:
            self.current_turn = 2
            self.player1.current_player = False
            self.player2.current_player = True
        else:
            self.current_turn = 1
            self.player1.current_player = True
            self.player2.current_player = False

    # def receive(self, player, row, col, info):
    #     # target player is the enemy of the player who sent the info
    #     if player == self.player1:
    #         target = self.player2
    #     else:
    #         target = self.player1
    #     # there is no other info cause of the return values. If we ere operating on Kafka,
    #     # the other type would be hit/miss or win
    #     if info == "fire":
    #         hit = target.receive_shot(row, col)
    #         print(hit)
    #         return hit


    def start_game(self):
        # set game phase to the shooting
        self.phase = 2

        # easier way of setting the first turn :)
        self.current_turn = 2
        self.next_turn()

        # change player boards from setup to the gaming ones
        self.player1.start_game()
        self.player2.start_game()


if __name__ == "__main__":
    game = GameLogic()
