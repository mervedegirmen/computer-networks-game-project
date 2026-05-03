from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class ResultDialog(QDialog):
    def __init__(self, winner, player_id, on_restart):
        super().__init__()

        self.on_restart = on_restart

        self.setWindowTitle("Game Over")
        self.setFixedSize(350, 220)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        if winner == player_id:
            result_text = "You Win!"
        else:
            result_text = "You Lose!"

        title_label = QLabel(result_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        winner_label = QLabel(f"Winner: Player {winner}")
        winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winner_label.setStyleSheet("font-size: 16px;")

        restart_button = QPushButton("Request Play Again")
        restart_button.setFixedHeight(40)
        restart_button.clicked.connect(self.restart_clicked)

        layout.addWidget(title_label)
        layout.addWidget(winner_label)
        layout.addWidget(restart_button)

        self.setLayout(layout)

    def restart_clicked(self):
        self.on_restart()
        self.close()