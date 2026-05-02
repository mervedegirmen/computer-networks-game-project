from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import Qt

from common.constants import DEFAULT_HOST, DEFAULT_PORT


class StartWindow(QWidget):
    def __init__(self, on_connect):
        super().__init__()

        self.on_connect = on_connect

        self.setWindowTitle("Snakes and Ladders - Start")
        self.setFixedSize(420, 300)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title_label = QLabel("Snakes and Ladders")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 26px; font-weight: bold;")

        subtitle_label = QLabel("Computer Networks Project")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 14px; color: gray;")

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Server IP Address")
        self.ip_input.setText(DEFAULT_HOST)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Server Port")
        self.port_input.setText(str(DEFAULT_PORT))

        self.connect_button = QPushButton("Connect to Server")
        self.connect_button.clicked.connect(self.connect_clicked)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(self.ip_input)
        layout.addWidget(self.port_input)
        layout.addWidget(self.connect_button)

        self.setLayout(layout)

    def connect_clicked(self):
        server_ip = self.ip_input.text().strip()
        port_text = self.port_input.text().strip()

        if not server_ip:
            QMessageBox.warning(self, "Input Error", "Please enter server IP address.")
            return

        if not port_text.isdigit():
            QMessageBox.warning(self, "Input Error", "Port must be a number.")
            return

        server_port = int(port_text)

        self.connect_button.setEnabled(False)
        self.connect_button.setText("Connecting...")

        self.on_connect(server_ip, server_port)

    def reset_button(self):
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect to Server")