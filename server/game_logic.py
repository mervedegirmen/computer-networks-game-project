import random

from common.constants import FINAL_SQUARE, SNAKES, LADDERS, PLAYER_1, PLAYER_2


class GameLogic:
    def __init__(self):
        self.reset_game()

    def reset_game(self):
        self.player_positions = {
            PLAYER_1: 0,
            PLAYER_2: 0,
        }

        self.extra_turn_used = {
            PLAYER_1: False,
            PLAYER_2: False,
        }


        self.current_turn = PLAYER_1
        self.game_over = False
        self.winner = None
        self.last_roll = None
        self.last_message = "Game started. Player 1 begins."

    def roll_for_player(self, player_id):
        if self.game_over:
            return {
                "success": False,
                "message": "Game is already over.",
            }

        if player_id != self.current_turn:
            return {
                "success": False,
                "message": f"It is not Player {player_id}'s turn.",
            }

        dice_value = random.randint(1, 6)
        self.last_roll = dice_value

        move_message = self.move_player(player_id, dice_value)

        if not self.game_over:
            if dice_value == 6 and not self.extra_turn_used[player_id]:
                self.extra_turn_used[player_id] = True
                self.last_message += f" Player {player_id} rolled 6 and gets one extra turn."
            else:
                self.extra_turn_used[player_id] = False
                self.switch_turn()

        return {
            "success": True,
            "dice": dice_value,
            "message": move_message,
        }

    def move_player(self, player_id, steps):
        current_position = self.player_positions[player_id]
        new_position = current_position + steps

        if new_position > FINAL_SQUARE:
            self.last_message = (
                f"Player {player_id} rolled {steps}, "
                f"but needs exact number to reach {FINAL_SQUARE}."
            )
            return self.last_message

        self.player_positions[player_id] = new_position

        message = (
            f"Player {player_id} rolled {steps} "
            f"and moved to square {new_position}."
        )

        final_position, extra_message = self.apply_snake_or_ladder(new_position)
        self.player_positions[player_id] = final_position

        if extra_message:
            message += " " + extra_message

        if final_position == FINAL_SQUARE:
            self.game_over = True
            self.winner = player_id
            message += f" Player {player_id} wins the game!"

        self.last_message = message
        return message

    def apply_snake_or_ladder(self, position):
        if position in SNAKES:
            new_position = SNAKES[position]
            message = (
                f"Snake! Player moved down "
                f"from square {position} to square {new_position}."
            )
            return new_position, message

        if position in LADDERS:
            new_position = LADDERS[position]
            message = (
                f"Ladder! Player climbed up "
                f"from square {position} to square {new_position}."
            )
            return new_position, message

        return position, ""

    def switch_turn(self):
        if self.current_turn == PLAYER_1:
            self.current_turn = PLAYER_2
        else:
            self.current_turn = PLAYER_1

    def get_state(self):
        return {
            "player_positions": self.player_positions,
            "current_turn": self.current_turn,
            "game_over": self.game_over,
            "winner": self.winner,
            "last_roll": self.last_roll,
            "last_message": self.last_message,
            "snakes": SNAKES,
            "ladders": LADDERS,
        }