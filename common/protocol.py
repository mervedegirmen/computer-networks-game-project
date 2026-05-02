import json


ASSIGN_PLAYER = "assign_player"
WAITING = "waiting"
GAME_START = "game_start"
ROLL_DICE = "roll_dice"
GAME_STATE = "game_state"
GAME_OVER = "game_over"
ERROR = "error"
RESTART_REQUEST = "restart_request"
OPPONENT_LEFT = "opponent_left"


def encode_message(data: dict) -> bytes:
    message = json.dumps(data)
    return (message + "\n").encode("utf-8")


def decode_message(message: str) -> dict:
    return json.loads(message)