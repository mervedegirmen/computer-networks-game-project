#burada pı girişi, port ihgitşi, main çinde yöntelicek

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

from common.constants import DEFAULT_HOST, DEFAULT_PORT


class StartWindow(QWidget):
    def __init__(self, on_connect_clicked=None):
        super().__init__()

        # Connect butonuna basılınca dışarıdan verilecek fonksiyonu saklıyoruz
        self.on_connect_clicked = on_connect_clicked

        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Snakes and Ladders - Start")
        self.resize(400, 200)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        title_label = QLabel("Snakes and Ladders")
        main_layout.addWidget(title_label)

        info_label = QLabel("Enter server information and connect.")
        main_layout.addWidget(info_label)

        # IP satırı
        ip_layout = QHBoxLayout()
        main_layout.addLayout(ip_layout)

        ip_label = QLabel("Server IP:")
        ip_layout.addWidget(ip_label)

        self.ip_input = QLineEdit()
        self.ip_input.setText(DEFAULT_HOST)
        ip_layout.addWidget(self.ip_input)

        # Port satırı
        port_layout = QHBoxLayout()
        main_layout.addLayout(port_layout)

        port_label = QLabel("Port:")
        port_layout.addWidget(port_label)

        self.port_input = QLineEdit()
        self.port_input.setText(str(DEFAULT_PORT))
        port_layout.addWidget(self.port_input)

        # Buton satırı
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.handle_connect_clicked)
        button_layout.addWidget(self.connect_button)

        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)

    def handle_connect_clicked(self):
        server_ip = self.ip_input.text().strip()
        port_text = self.port_input.text().strip()

        if not server_ip:
            QMessageBox.warning(self, "Error", "Server IP cannot be empty.")
            return

        if not port_text:
            QMessageBox.warning(self, "Error", "Port cannot be empty.")
            return

        try:
            server_port = int(port_text)
        except ValueError:
            QMessageBox.warning(self, "Error", "Port must be a number.")
            return

        if self.on_connect_clicked:
            self.on_connect_clicked(server_ip, server_port)

    def set_connect_enabled(self, enabled: bool):
        self.connect_button.setEnabled(enabled)