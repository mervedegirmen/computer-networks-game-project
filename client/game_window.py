from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)

from client.board_widget import BoardWidget
from common.protocol import ROLL_DICE


class GameWindow(QWidget):
    def __init__(self, network_client):
        super().__init__()

        self.network_client = network_client
        self.player_id = None
        self.current_turn = None
        self.game_over = False

        self.setWindowTitle("Snakes and Ladders")
        self.resize(950, 750)

        main_layout = QHBoxLayout()

        self.board = BoardWidget()

        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_panel.setSpacing(15)

        self.title_label = QLabel("Snakes and Ladders")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.player_label = QLabel("Player: -")
        self.player_label.setStyleSheet("font-size: 16px;")

        self.turn_label = QLabel("Turn: -")
        self.turn_label.setStyleSheet("font-size: 16px;")

        self.dice_label = QLabel("Dice: -")
        self.dice_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.roll_button = QPushButton("Roll Dice")
        self.roll_button.setFixedHeight(45)
        self.roll_button.setEnabled(False)
        self.roll_button.clicked.connect(self.roll_dice)

        self.message_box = QTextEdit()
        self.message_box.setReadOnly(True)
        self.message_box.setMinimumHeight(250)

        right_panel.addWidget(self.title_label)
        right_panel.addWidget(self.player_label)
        right_panel.addWidget(self.turn_label)
        right_panel.addWidget(self.dice_label)
        right_panel.addWidget(self.roll_button)
        right_panel.addWidget(QLabel("Game Messages:"))
        right_panel.addWidget(self.message_box)

        main_layout.addWidget(self.board, stretch=4)
        main_layout.addLayout(right_panel, stretch=1)

        self.setLayout(main_layout)

    def set_player_id(self, player_id):
        self.player_id = player_id
        self.player_label.setText(f"Player: {player_id}")
        self.add_message(f"You are Player {player_id}.")

    def update_game_state(self, state):
        positions = state.get("player_positions", {})
        self.current_turn = state.get("current_turn")
        self.game_over = state.get("game_over", False)

        self.board.update_board(positions)

        self.turn_label.setText(f"Turn: Player {self.current_turn}")

        last_roll = state.get("last_roll")
        if last_roll is not None:
            self.dice_label.setText(f"Dice: {last_roll}")

        last_message = state.get("last_message")
        if last_message:
            self.add_message(last_message)

        self.update_roll_button()

    def update_roll_button(self):
        if self.game_over:
            self.roll_button.setEnabled(False)
            self.roll_button.setText("Game Over")
            return

        if self.player_id == self.current_turn:
            self.roll_button.setEnabled(True)
            self.roll_button.setText("Roll Dice")
        else:
            self.roll_button.setEnabled(False)
            self.roll_button.setText("Opponent's Turn")

    def roll_dice(self):
        self.roll_button.setEnabled(False)

        self.network_client.send_message({
            "type": ROLL_DICE
        })

    def add_message(self, message):
        self.message_box.append(message)