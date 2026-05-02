import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from PyQt6.QtWidgets import QApplication, QMessageBox

from client.start_window import StartWindow
from client.game_window import GameWindow
from client.network import NetworkClient
from client.result_dialog import ResultDialog

from common.protocol import (
    ASSIGN_PLAYER,
    WAITING,
    GAME_START,
    GAME_STATE,
    GAME_OVER,
    ERROR,
    RESTART_REQUEST,
    OPPONENT_LEFT,
)


class ClientApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.network_client = NetworkClient()

        self.start_window = StartWindow(self.connect_to_server)
        self.game_window = GameWindow(self.network_client)

        self.player_id = None
        self.result_dialog = None

        self.network_client.connection_success.connect(self.connection_success)
        self.network_client.connection_error.connect(self.connection_error)
        self.network_client.message_received.connect(self.handle_server_message)

    def run(self):
        self.start_window.show()
        sys.exit(self.app.exec())

    def connect_to_server(self, server_ip, server_port):
        self.network_client.connect_to_server(server_ip, server_port)

    def connection_success(self):
        self.start_window.hide()
        self.game_window.show()

    def connection_error(self, error_message):
        QMessageBox.critical(
            self.start_window,
            "Connection Error",
            error_message
        )

        self.start_window.reset_button()

    def handle_server_message(self, message):
        message_type = message.get("type")

        if message_type == ASSIGN_PLAYER:
            self.player_id = message.get("player_id")
            self.game_window.set_player_id(self.player_id)

        elif message_type == WAITING:
            self.game_window.add_message(message.get("message", "Waiting..."))

        elif message_type == GAME_START:
            self.game_window.add_message(message.get("message", "Game started."))

            state = message.get("state")
            if state:
                self.game_window.update_game_state(state)

        elif message_type == GAME_STATE:
            state = message.get("state")
            if state:
                self.game_window.update_game_state(state)

        elif message_type == GAME_OVER:
            state = message.get("state")
            winner = message.get("winner")

            if state:
                self.game_window.update_game_state(state)

            self.show_result_dialog(winner)

        elif message_type == ERROR:
            QMessageBox.warning(
                self.game_window,
                "Game Error",
                message.get("message", "Unknown error.")
            )

        elif message_type == OPPONENT_LEFT:
            QMessageBox.warning(
                self.game_window,
                "Opponent Left",
                message.get("message", "Opponent left the game.")
            )

    def show_result_dialog(self, winner):
        if self.result_dialog is not None:
            return

        self.result_dialog = ResultDialog(
            winner=winner,
            player_id=self.player_id,
            on_restart=self.restart_game
        )

        self.result_dialog.exec()
        self.result_dialog = None

    def restart_game(self):
        self.network_client.send_message({
            "type": RESTART_REQUEST
        })


if __name__ == "__main__":
    client_app = ClientApp()
    client_app.run()