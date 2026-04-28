import os
import sys

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox

# Proje ana klasörünü Python path'ine ekliyoruz
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from network import ClientNetwork
from game_window import GameWindow
from common.constants import DEFAULT_HOST, DEFAULT_PORT
from common.protocol import (
    ROLL_DICE,
    GAME_START,
    GAME_STATE,
    GAME_OVER,
    ASSIGN_PLAYER,
    WAITING,
    ERROR,
    OPPONENT_LEFT
)


class ClientApp(GameWindow):
    # Arka thread'den gelen mesajı ana thread'e güvenli şekilde taşımak için signal
    server_message_signal = pyqtSignal(dict)

    # Bağlantı kopunca ana thread'e güvenli şekilde bilgi taşımak için signal
    disconnected_signal = pyqtSignal()

    def __init__(self):
        # Önce GameWindow'u kuruyoruz
        super().__init__(
            on_roll_clicked=self.roll_dice,
            on_disconnect_clicked=self.disconnect_from_server
        )

        # Ağ sınıfını oluşturuyoruz
        self.network = ClientNetwork(
            on_message_received=self.on_network_message,
            on_disconnected=self.on_network_disconnected
        )

        # Oyuncu numarası başlangıçta belli değil
        self.player_id = None

        # Signal-slot bağlantıları
        self.server_message_signal.connect(self.handle_server_message)
        self.disconnected_signal.connect(self.handle_disconnect)

        # Şimdilik oyun ekranını açıyoruz ve otomatik bağlanıyoruz
        self.auto_connect()

    def auto_connect(self):
        """
        Şimdilik başlangıç ekranı kullanmadan otomatik bağlanıyoruz.
        Sonra start_window eklersek bu kısmı değiştireceğiz.
        """
        success, message = self.network.connect_to_server(DEFAULT_HOST, DEFAULT_PORT)

        if success:
            self.append_message("Connected to server.")
            self.set_waiting_mode()
        else:
            QMessageBox.critical(self, "Connection Error", message)

    def on_network_message(self, data):
        """
        Network thread burayı çağırır.
        Burada doğrudan UI güncellemiyoruz; signal ile ana thread'e taşıyoruz.
        """
        self.server_message_signal.emit(data)

    def on_network_disconnected(self):
        """
        Network thread bağlantı koptuğunda burayı çağırır.
        """
        self.disconnected_signal.emit()

    def handle_server_message(self, data):
        """
        Sunucudan gelen mesaj tipine göre arayüzü güncelliyoruz.
        """
        message_type = data.get("type")

        if message_type == ASSIGN_PLAYER:
            self.player_id = data.get("player_id")
            self.set_player_id(self.player_id)
            self.append_message(data.get("message", "Assigned player."))

        elif message_type == WAITING:
            self.append_message(data.get("message", "Waiting for the other player..."))
            self.set_waiting_mode()

        elif message_type == GAME_START:
            self.append_message(data.get("message", "Game started."))
            state = data.get("state", {})
            self.update_game_state(state)

        elif message_type == GAME_STATE:
            state = data.get("state", {})
            self.update_game_state(state)

        elif message_type == GAME_OVER:
            state = data.get("state", {})
            self.update_game_state(state)

            winner = data.get("winner")
            self.append_message(data.get("message", "Game over."))

            if winner == self.player_id:
                QMessageBox.information(self, "Game Over", "You won the game!")
            else:
                QMessageBox.information(self, "Game Over", "You lost the game!")

        elif message_type == ERROR:
            self.append_message("Error: " + data.get("message", "Unknown error"))

        elif message_type == OPPONENT_LEFT:
            self.append_message(data.get("message", "Opponent disconnected."))
            self.set_waiting_mode()

        else:
            self.append_message(f"Unknown message received: {data}")

    def roll_dice(self):
        """
        Roll Dice butonuna basılınca sunucuya zar atma isteği gönderiyoruz.
        """
        success = self.network.send_message({
            "type": ROLL_DICE
        })

        if not success:
            QMessageBox.warning(self, "Error", "Could not send roll request.")

    def handle_disconnect(self):
        """
        Bağlantı koptuğunda ekranı güncelliyoruz.
        """
        self.status_label.setText("Disconnected")
        self.roll_button.setEnabled(False)
        self.append_message("Disconnected from server.")

    def disconnect_from_server(self):
        """
        Kullanıcı Disconnect derse bağlantıyı kapatıyoruz.
        """
        self.network.close_connection()
        self.handle_disconnect()

    def closeEvent(self, event):
        """
        Pencere kapanırken socket temiz kapansın.
        """
        self.network.close_connection()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ClientApp()
    window.show()

    sys.exit(app.exec())