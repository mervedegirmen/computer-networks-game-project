import socket
from threading import Thread

from PyQt6.QtCore import QObject, pyqtSignal

from common.protocol import encode_message, decode_message


class NetworkClient(QObject):
    message_received = pyqtSignal(dict)
    connection_success = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.listen_thread = None
        self.running = False

    def connect_to_server(self, server_ip, server_port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, server_port))

            self.running = True
            self.connection_success.emit()

            self.listen_thread = Thread(target=self.listen_server)
            self.listen_thread.daemon = True
            self.listen_thread.start()

        except Exception as error:
            self.connection_error.emit(str(error))

    def listen_server(self):
        buffer = ""

        while self.running and self.client_socket:
            try:
                data = self.client_socket.recv(1024)

                if not data:
                    self.connection_error.emit("Server connection closed.")
                    self.close_connection()
                    return

                buffer += data.decode("utf-8")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if line.strip():
                        message = decode_message(line)
                        self.message_received.emit(message)

            except Exception as error:
                self.connection_error.emit(str(error))
                self.close_connection()
                return

    def send_message(self, message):
        if self.client_socket:
            try:
                self.client_socket.sendall(encode_message(message))
            except Exception as error:
                self.connection_error.emit(str(error))

    def close_connection(self):
        self.running = False

        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass

            self.client_socket = None