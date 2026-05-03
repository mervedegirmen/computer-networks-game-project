import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import socket
from threading import Thread

from common.constants import DEFAULT_PORT, MAX_PLAYERS
from common.protocol import (
    ASSIGN_PLAYER,
    WAITING,
    GAME_START,
    ROLL_DICE,
    GAME_STATE,
    GAME_OVER,
    ERROR,
    RESTART_REQUEST,
    OPPONENT_LEFT,
    encode_message,
    decode_message,
    RESTART_WAITING,
)

from game_logic import GameLogic


class GameServer:
    def __init__(self, host="", port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.game = GameLogic()
        self.running = True
        self.restart_votes = set()

    def start(self):
        print("[SERVER] Starting server...")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(MAX_PLAYERS)

        print(f"[SERVER] Server started on port {self.port}")
        print("[SERVER] Waiting for players...")

        while self.running:
            client_socket, client_address = self.server_socket.accept()

            if len(self.clients) >= MAX_PLAYERS:
                client_socket.sendall(
                    encode_message({
                        "type": ERROR,
                        "message": "Game is full."
                    })
                )
                client_socket.close()
                continue

            player_id = len(self.clients) + 1
            self.clients[player_id] = client_socket

            print(f"[SERVER] Player {player_id} connected from {client_address}")

            client_socket.sendall(
                encode_message({
                    "type": ASSIGN_PLAYER,
                    "player_id": player_id
                })
            )

            if len(self.clients) < MAX_PLAYERS:
                client_socket.sendall(
                    encode_message({
                        "type": WAITING,
                        "message": "Waiting for second player..."
                    })
                )
            else:
                self.broadcast({
                    "type": GAME_START,
                    "message": "Both players connected. Game started!",
                    "state": self.game.get_state()
                })

            thread = Thread(target=self.handle_client, args=(player_id,))
            thread.daemon = True
            thread.start()

    def handle_client(self, player_id):
        client_socket = self.clients[player_id]
        buffer = ""

        while self.running:
            try:
                data = client_socket.recv(1024)

                if not data:
                    break

                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    message = decode_message(line)
                    self.process_message(player_id, message)

            except ConnectionError:
                break
            except Exception as error:
                print(f"[SERVER] Error for Player {player_id}: {error}")
                break

        self.remove_client(player_id)

    def process_message(self, player_id, message):
        message_type = message.get("type")

        if message_type == ROLL_DICE:
            result = self.game.roll_for_player(player_id)

            if not result["success"]:
                self.send_to_player(player_id, {
                    "type": ERROR,
                    "message": result["message"]
                })
                return

            state = self.game.get_state()

            self.broadcast({
                "type": GAME_STATE,
                "state": state
            })

            if state["game_over"]:
                self.broadcast({
                    "type": GAME_OVER,
                    "winner": state["winner"],
                    "state": state
                })


        elif message_type == RESTART_REQUEST:

            if not self.game.game_over:
                self.send_to_player(player_id, {

                    "type": ERROR,

                    "message": "Game is not over yet."

                })

                return

            self.restart_votes.add(player_id)

            if len(self.restart_votes) < MAX_PLAYERS:
                self.broadcast({

                    "type": RESTART_WAITING,

                    "message": f"Player {player_id} wants to play again. Waiting for other player..."

                })

                return

            self.restart_votes.clear()

            self.game.reset_game()

            self.broadcast({

                "type": GAME_START,

                "message": "Both players accepted. New game started!",

                "state": self.game.get_state()

            })

    def send_to_player(self, player_id, message):
        if player_id in self.clients:
            self.clients[player_id].sendall(encode_message(message))

    def broadcast(self, message):
        for client_socket in self.clients.values():
            client_socket.sendall(encode_message(message))

    def remove_client(self, player_id):
        print(f"[SERVER] Player {player_id} disconnected.")

        if player_id in self.clients:
            try:
                self.clients[player_id].close()
            except Exception:
                pass

            del self.clients[player_id]

        self.restart_votes.discard(player_id)

        if len(self.clients) == 0:
            print("[SERVER] All players disconnected. Game reset.")
            self.game.reset_game()
            self.restart_votes.clear()
            return

        self.broadcast({
            "type": OPPONENT_LEFT,
            "message": f"Player {player_id} left the game."
        })


if __name__ == "__main__":
    server = GameServer()
    server.start()