#buraadaki kod da clientları ve mesajlari yonetecek
#Socket ile ağ bağlantısı kurmak için gerekli kod bloğu
import os
import sys
# Socket ile TCP sunucu kurmak için gerekli modül.
import socket

# Aynı anda birden fazla istemciyi yönetmek için thread kullanacağız.
from threading import Thread, Lock

# Daha okunaklı tip ipuçları için Optional kullanıyoruz.
from typing import Optional
# Proje ana klasörünü Python path'ine ekliyoruz.
# Böylece common klasörünü görebilir.
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Oyunun kurallarını yöneten sınıfı içe aktarıyoruz.
from game_logic import GameLogic

# Ortak sabitleri alıyoruz.
from common.constants import DEFAULT_HOST, DEFAULT_PORT, MAX_PLAYERS

# Protokolde tanımladığımız mesaj tiplerini ve yardımcı fonksiyonları içe aktarıyoruz.
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
    decode_message
)


# Bu sınıf bütün sunucu davranışını yönetecek.
class SnakeLaddersServer:
    # Sınıf oluşturulunca ilk çalışan fonksiyon.
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        # Sunucunun IP bilgisi.
        self.host = host

        # Sunucunun port bilgisi.
        self.port = port

        # Ana server socket başlangıçta yok.
        self.server_socket: Optional[socket.socket] = None

        # Oyuncu 1'in socket bağlantısı burada tutulacak.
        self.player1_socket: Optional[socket.socket] = None

        # Oyuncu 2'nin socket bağlantısı burada tutulacak.
        self.player2_socket: Optional[socket.socket] = None

        # Oyunun kurallarını yöneten nesneyi oluşturuyoruz.
        self.game = GameLogic()

        # Aynı anda iki thread kritik veri değiştirmesin diye lock kullanıyoruz.
        self.lock = Lock()

    # Bu fonksiyon verilen oyuncu numarasına ait socket'i döndürür.
    def get_player_socket(self, player_id):
        # Eğer oyuncu 1 isteniyorsa player1_socket döndür.
        if player_id == 1:
            return self.player1_socket

        # Eğer oyuncu 2 isteniyorsa player2_socket döndür.
        if player_id == 2:
            return self.player2_socket

        # Geçersiz oyuncu numarası ise None döndür.
        return None

    # Bu fonksiyon verilen oyuncu numarasına ait socket'i kaydeder.
    def set_player_socket(self, player_id, client_socket):
        # Oyuncu 1 ise player1_socket içine koy.
        if player_id == 1:
            self.player1_socket = client_socket

        # Oyuncu 2 ise player2_socket içine koy.
        elif player_id == 2:
            self.player2_socket = client_socket

    # Bu fonksiyon o anda bağlı oyuncu sayısını döndürür.
    def connected_player_count(self):
        # Başlangıçta sayaç 0.
        count = 0

        # Eğer oyuncu 1 bağlıysa sayacı artır.
        if self.player1_socket is not None:
            count += 1

        # Eğer oyuncu 2 bağlıysa sayacı artır.
        if self.player2_socket is not None:
            count += 1

        # Toplam bağlı oyuncu sayısını döndür.
        return count

    # Bu fonksiyon ilk boş oyuncu numarasını bulur.
    def get_available_player_id(self):
        # Eğer oyuncu 1 boşsa önce onu ver.
        if self.player1_socket is None:
            return 1

        # Eğer oyuncu 2 boşsa onu ver.
        if self.player2_socket is None:
            return 2

        # İkisi de doluysa boş yer yok.
        return None

    # Bu fonksiyon tek bir oyuncuya mesaj gönderir.
    def send_to_player(self, player_id, message_dict):
        # Oyuncunun socket'ini buluyoruz.
        client_socket = self.get_player_socket(player_id)

        # Eğer socket varsa mesajı gönderiyoruz.
        if client_socket:
            try:
                # Sözlüğü JSON + byte haline getirip gönderiyoruz.
                client_socket.sendall(encode_message(message_dict))
            except Exception as e:
                # Gönderim hatası olursa bilgi yazdırıyoruz.
                print(f"[SERVER] Error sending to Player {player_id}: {e}")

                # Oyuncuyu bağlantıdan çıkarıyoruz.
                self.remove_player(player_id)

    # Bu fonksiyon iki oyuncuya da aynı mesajı gönderir.
    def broadcast(self, message_dict):
        # Oyuncu 1 bağlıysa ona gönder.
        if self.player1_socket:
            self.send_to_player(1, message_dict)

        # Oyuncu 2 bağlıysa ona gönder.
        if self.player2_socket:
            self.send_to_player(2, message_dict)

    # Bu fonksiyon oyuncu bağlantısını sistemden kaldırır.
    def remove_player(self, player_id):
        # Kritik işlem olduğu için lock kullanıyoruz.
        with self.lock:
            # İlgili oyuncunun socket'ini alıyoruz.
            client_socket = self.get_player_socket(player_id)

            # Eğer socket varsa kapatıyoruz.
            if client_socket:
                try:
                    client_socket.close()
                except Exception:
                    pass

            # O oyuncunun socket alanını boşaltıyoruz.
            self.set_player_socket(player_id, None)

            # Oyunu sıfırlıyoruz çünkü iki oyunculu yapıda biri gidince oyun devam etmemeli.
            self.game.reset_game()

            # Diğer oyuncuya rakibin çıktığını bildiriyoruz.
            self.broadcast({
                "type": OPPONENT_LEFT,
                "message": f"Player {player_id} disconnected. Waiting for a new player..."
            })

    # Bu fonksiyon oyuna başlanabilecek durumdaysak game_start mesajı yollar.
    def try_start_game(self):
        # Eğer iki oyuncu da bağlıysa oyunu başlatıyoruz.
        if self.player1_socket is not None and self.player2_socket is not None:
            # Oyunu temiz başlangıç durumuna getiriyoruz.
            self.game.reset_game()

            # Herkese oyun başladı mesajı gönderiyoruz.
            self.broadcast({
                "type": GAME_START,
                "message": "Both players connected. Game is starting.",
                "state": self.game.get_state()
            })

            # Konsola da bilgi yazıyoruz.
            print("[SERVER] Both players connected. Game started.")

    # Bu fonksiyon yeni istemcileri kabul eder.
    def accept_connections(self):
        # Sonsuz döngü ile sürekli bağlantı bekliyoruz.
        while True:
            # Yeni istemci bağlanınca accept ile socket ve adres bilgisi alıyoruz.
            client_socket, client_address = self.server_socket.accept()

            print(f"[SERVER] New connection from {client_address}")

            # Bağlantı atama kısmı kritik olduğu için lock içine alıyoruz.
            with self.lock:
                # Boş oyuncu numarasını buluyoruz.
                player_id = self.get_available_player_id()

                # Eğer boş yer yoksa server doludur.
                if player_id is None:
                    # Yeni gelen istemciye hata mesajı gönderiyoruz.
                    client_socket.sendall(encode_message({
                        "type": ERROR,
                        "message": "Server is full. Two players are already connected."
                    }))

                    # Sonra bağlantıyı kapatıyoruz.
                    client_socket.close()

                    print("[SERVER] Rejected extra client because server is full.")
                    continue

                # Yeni bağlanan istemciyi uygun oyuncu numarasına yerleştiriyoruz.
                self.set_player_socket(player_id, client_socket)

            # Bağlanan oyuncuya kendi oyuncu numarasını bildiriyoruz.
            self.send_to_player(player_id, {
                "type": ASSIGN_PLAYER,
                "player_id": player_id,
                "message": f"You are Player {player_id}."
            })

            # Eğer henüz iki oyuncu tamam değilse bekleme mesajı gönderiyoruz.
            if self.connected_player_count() < MAX_PLAYERS:
                self.send_to_player(player_id, {
                    "type": WAITING,
                    "message": "Waiting for the other player..."
                })

            # Bu istemciyi dinlemek için ayrı thread başlatıyoruz.
            listen_thread = Thread(
                target=self.message_listen_thread,
                args=(client_socket, player_id)
            )
            listen_thread.start()

            # Eğer artık iki oyuncu da bağlandıysa oyunu başlatmayı deniyoruz.
            self.try_start_game()

    # Bu fonksiyon istemciden gelen mesajları dinler.
    def message_listen_thread(self, client_socket, player_id):
        print(f"[SERVER] Listener thread started for Player {player_id}")

        try:
            # Socket'i satır satır okuyabilmek için dosya benzeri hale getiriyoruz.
            socket_file = client_socket.makefile("r", encoding="utf-8")

            while self.get_player_socket(player_id):
                # Bir satır = bir JSON mesajı
                line = socket_file.readline()

                # Boş satır geldiyse bağlantı kopmuş olabilir.
                if not line:
                    print(f"[SERVER] Empty message received from Player {player_id}")
                    self.remove_player(player_id)
                    return

                try:
                    # Satırı JSON'dan sözlüğe çeviriyoruz.
                    data = decode_message(line.strip())
                except Exception as e:
                    # Hatalı mesaj geldiyse sadece o oyuncuya hata dönüyoruz.
                    self.send_to_player(player_id, {
                        "type": ERROR,
                        "message": f"Invalid message format: {e}"
                    })
                    continue

                # Mesaj tipini alıyoruz.
                message_type = data.get("type")

                print(f"[SERVER] Received from Player {player_id}: {data}")

                # Oyuncu zar atmak istiyorsa
                if message_type == ROLL_DICE:
                    with self.lock:
                        result = self.game.roll_for_player(player_id)

                        # Hatalı bir durum varsa sadece o oyuncuya hata gönder
                        if not result["success"]:
                            self.send_to_player(player_id, {
                                "type": ERROR,
                                "message": result["message"]
                            })
                            continue

                        # Herkese güncel oyun durumunu gönder
                        self.broadcast({
                            "type": GAME_STATE,
                            "state": self.game.get_state()
                        })

                        # Oyun bittiyse ayrıca game_over gönder
                        if self.game.game_over:
                            self.broadcast({
                                "type": GAME_OVER,
                                "winner": self.game.winner,
                                "message": self.game.last_message,
                                "state": self.game.get_state()
                            })

                # Oyunu yeniden başlatma isteği geldiyse
                elif message_type == RESTART_REQUEST:
                    with self.lock:
                        self.game.reset_game()
                        self.broadcast({
                            "type": GAME_START,
                            "message": "Game restarted.",
                            "state": self.game.get_state()
                        })

                # Tanınmayan mesaj tipi gelirse
                else:
                    self.send_to_player(player_id, {
                        "type": ERROR,
                        "message": "Unknown message type."
                    })

        except Exception as error:
            print(f"[SERVER] Error while handling Player {player_id}: {error}")
            self.remove_player(player_id)
    # Bu fonksiyon sunucuyu başlatır.
    def start_server(self):
        print("[SERVER] Starting server...")

        # TCP socket oluşturuyoruz.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Port tekrar kullanımını kolaylaştırıyoruz.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Sunucuyu host ve porta bağlıyoruz.
        self.server_socket.bind((self.host, self.port))

        # İstemci bağlantılarını dinlemeye başlıyoruz.
        self.server_socket.listen()

        print(f"[SERVER] Server started on {self.host}:{self.port}")
        print("[SERVER] Waiting for players...")

        # Yeni bağlantıları kabul etmeye başlıyoruz.
        self.accept_connections()


# Bu dosya doğrudan çalıştırılırsa burası çalışır.
if __name__ == "__main__":
    # Sunucu nesnesi oluşturuyoruz.
    server = SnakeLaddersServer()

    # Sunucuyu başlatıyoruz.
    server.start_server()

