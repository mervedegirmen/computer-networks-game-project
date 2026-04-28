from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QGridLayout,
    QFrame
)
from PyQt6.QtCore import Qt


class GameWindow(QWidget):
    def __init__(self, on_roll_clicked=None, on_disconnect_clicked=None):
        super().__init__()

        self.on_roll_clicked = on_roll_clicked
        self.on_disconnect_clicked = on_disconnect_clicked

        self.player_id = None
        self.current_turn = None

        # Her kare için widget referanslarını tutacağız
        self.cell_widgets = {}

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Snakes and Ladders - Game")
        self.resize(1000, 700)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Sol taraf: tahta
        board_container = QWidget()
        self.board_layout = QGridLayout()
        self.board_layout.setSpacing(2)
        board_container.setLayout(self.board_layout)

        main_layout.addWidget(board_container, 2)

        # Sağ taraf: bilgi ve kontroller
        side_panel = QWidget()
        side_layout = QVBoxLayout()
        side_panel.setLayout(side_layout)

        main_layout.addWidget(side_panel, 1)

        self.status_label = QLabel("Game not started")
        side_layout.addWidget(self.status_label)

        self.player_label = QLabel("Player: Unknown")
        side_layout.addWidget(self.player_label)

        self.positions_label = QLabel("P1: 0 | P2: 0")
        side_layout.addWidget(self.positions_label)

        self.last_roll_label = QLabel("Last Roll: -")
        side_layout.addWidget(self.last_roll_label)

        self.last_message_label = QLabel("Last Message: -")
        self.last_message_label.setWordWrap(True)
        side_layout.addWidget(self.last_message_label)

        self.message_list = QListWidget()
        side_layout.addWidget(self.message_list)

        self.roll_button = QPushButton("Roll Dice")
        self.roll_button.clicked.connect(self.handle_roll_clicked)
        self.roll_button.setEnabled(False)
        side_layout.addWidget(self.roll_button)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.handle_disconnect_clicked)
        side_layout.addWidget(self.disconnect_button)

        self.create_board()

    def create_board(self):
        """
        10x10 Yılanlar ve Merdivenler tahtasını oluşturur.
        Numara yerleşimi klasik zigzag mantığında yapılır:
        alt sıra soldan sağa,
        bir üst sıra sağdan sola...
        """
        for row in range(10):
            for col in range(10):
                cell_frame = QFrame()
                cell_frame.setFrameShape(QFrame.Shape.Box)
                cell_frame.setLineWidth(1)
                cell_frame.setMinimumSize(60, 60)

                cell_layout = QVBoxLayout()
                cell_layout.setContentsMargins(4, 4, 4, 4)
                cell_frame.setLayout(cell_layout)

                square_number = self.get_square_number(row, col)

                number_label = QLabel(str(square_number))
                number_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

                token_label = QLabel("")
                token_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                token_label.setWordWrap(True)

                cell_layout.addWidget(number_label)
                cell_layout.addStretch()
                cell_layout.addWidget(token_label)

                # Yılan ve merdiven karelerini hafif renklendir
                if square_number in [16, 47, 49, 56, 62, 64, 87, 93, 95, 98]:
                    cell_frame.setStyleSheet("background-color: #3a1f1f;")
                elif square_number in [1, 4, 9, 21, 28, 36, 51, 71, 80]:
                    cell_frame.setStyleSheet("background-color: #1f3a25;")
                else:
                    cell_frame.setStyleSheet("background-color: #2b2b2b;")

                self.board_layout.addWidget(cell_frame, row, col)

                self.cell_widgets[square_number] = {
                    "frame": cell_frame,
                    "number_label": number_label,
                    "token_label": token_label
                }

    def get_square_number(self, row, col):
        """
        Grid satır-sütun bilgisinden oyun karesini hesaplar.
        row=9 alt satır, row=0 üst satır olacak şekilde görünür.
        """
        visual_row_from_bottom = 9 - row
        base = visual_row_from_bottom * 10

        if visual_row_from_bottom % 2 == 0:
            return base + col + 1
        else:
            return base + (10 - col)

    def set_player_id(self, player_id: int):
        self.player_id = player_id
        self.player_label.setText(f"Player: {player_id}")

    def update_game_state(self, state: dict):
        positions = state.get("player_positions", {})
        current_turn = state.get("current_turn")
        last_roll = state.get("last_roll")
        last_message = state.get("last_message", "")
        game_over = state.get("game_over", False)

        player1_pos = positions.get("1", positions.get(1, 0))
        player2_pos = positions.get("2", positions.get(2, 0))

        self.current_turn = current_turn

        self.positions_label.setText(f"P1: {player1_pos} | P2: {player2_pos}")
        self.last_roll_label.setText(f"Last Roll: {last_roll if last_roll is not None else '-'}")
        self.last_message_label.setText(f"Last Message: {last_message if last_message else '-'}")

        if last_message:
            self.message_list.addItem(last_message)

        self.draw_tokens(player1_pos, player2_pos)

        if game_over:
            self.status_label.setText("Game Over")
            self.roll_button.setEnabled(False)
            return

        if self.player_id == current_turn:
            self.status_label.setText("Your turn")
            self.roll_button.setEnabled(True)
        else:
            self.status_label.setText("Opponent's turn")
            self.roll_button.setEnabled(False)

    def draw_tokens(self, player1_pos: int, player2_pos: int):
        # Önce bütün karelerdeki token yazılarını temizle
        for square in self.cell_widgets:
            self.cell_widgets[square]["token_label"].setText("")

        # Oyuncular 0'daysa tahtaya yerleştirmiyoruz
        position_map = {}

        if player1_pos > 0:
            position_map.setdefault(player1_pos, []).append("P1")

        if player2_pos > 0:
            position_map.setdefault(player2_pos, []).append("P2")

        for square, players in position_map.items():
            if square in self.cell_widgets:
                self.cell_widgets[square]["token_label"].setText(" | ".join(players))

    def handle_roll_clicked(self):
        self.roll_button.setEnabled(False)

        if self.on_roll_clicked:
            self.on_roll_clicked()

    def handle_disconnect_clicked(self):
        if self.on_disconnect_clicked:
            self.on_disconnect_clicked()

    def append_message(self, text: str):
        self.message_list.addItem(text)

    def set_waiting_mode(self):
        self.status_label.setText("Waiting for the other player...")
        self.roll_button.setEnabled(False)