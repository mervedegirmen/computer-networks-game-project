import os  # Dosya ve klasör yolları ile çalışmak için os modülünü içe aktarır.
import sys  # Python çalışma ortamı ve import yolları işlemleri için sys modülünü içe aktarır.

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Bu dosyanın bulunduğu server klasörünün tam yolunu alır.
PROJECT_DIR = os.path.dirname(CURRENT_DIR)  # Proje ana klasörünün yolunu alır.

if PROJECT_DIR not in sys.path:  # Proje klasörü Python import yollarında yoksa kontrol eder.
    sys.path.insert(0, PROJECT_DIR)  # Proje klasörünü import yollarına ekler.

import socket  # TCP/IP soket bağlantıları için socket modülünü içe aktarır.
from threading import Thread  # Her oyuncuyu ayrı thread üzerinde çalıştırmak için Thread sınıfını içe aktarır.
import requests  # HTTP istekleri göndermek için requests modülünü içe aktarır.

from common.constants import DEFAULT_PORT, MAX_PLAYERS  # Varsayılan port ve maksimum oyuncu sayısını içe aktarır.
from common.protocol import (  # Client-server mesajlaşma protokolündeki mesaj tiplerini ve yardımcı fonksiyonları içe aktarır.
    ASSIGN_PLAYER,  # Oyuncuya ID atama mesaj tipi.
    WAITING,  # Bekleme mesaj tipi.
    GAME_START,  # Oyun başlangıç mesaj tipi.
    ROLL_DICE,  # Zar atma mesaj tipi.
    GAME_STATE,  # Güncel oyun durumu mesaj tipi.
    GAME_OVER,  # Oyun bitiş mesaj tipi.
    ERROR,  # Hata mesaj tipi.
    RESTART_REQUEST,  # Tekrar oynama isteği mesaj tipi.
    OPPONENT_LEFT,  # Rakibin ayrıldığını belirten mesaj tipi.
    encode_message,  # Python dict mesajlarını JSON byte formatına çeviren fonksiyon.
    decode_message,  # JSON mesajlarını Python dict tipine çeviren fonksiyon.
    RESTART_WAITING,  # Tekrar oynama için diğer oyuncunun beklendiğini belirten mesaj tipi.
)

from game_logic import GameLogic  # Oyunun tüm mantığını yöneten GameLogic sınıfını içe aktarır.


class GameServer:  # Server tarafındaki bağlantıları ve oyun yönetimini gerçekleştiren ana sınıftır.
    def __init__(self, host="", port=DEFAULT_PORT):  # Server nesnesi oluşturulurken çalışan kurucu metottur.
        self.host = host  # Server'ın dinleyeceği IP adresini saklar.
        self.port = port  # Server'ın kullanacağı port numarasını saklar.
        self.server_socket = None  # Ana server socket nesnesini başlangıçta boş tutar.
        self.clients = {}  # Bağlı oyuncuların socket bilgilerini tutan sözlüktür.
        self.game = GameLogic()  # Oyun kurallarını yönetecek GameLogic nesnesini oluşturur.
        self.running = True  # Server ana döngüsünün çalışıp çalışmadığını kontrol eder.
        self.restart_votes = set()  # Tekrar oynama isteyen oyuncuları tutan kümedir.


    def start(self):  # Server'ı başlatır ve client bağlantılarını kabul etmeye başlar.
        print("[SERVER] Starting server...")  # Konsola server başlatılıyor mesajı yazdırır.

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 ve TCP kullanan server socket oluşturur.
        self.server_socket.bind((self.host, self.port))  # Socket'i belirtilen host ve port'a bağlar.
        self.server_socket.listen(MAX_PLAYERS)  # Maksimum oyuncu sayısı kadar bağlantıyı dinlemeye başlar.

        print(f"[SERVER] Server started on port {self.port}")  # Server'ın hangi portta çalıştığını konsola yazdırır.
        print("[SERVER] Waiting for players...")  # Oyuncuların beklenildiğini konsola yazdırır.


        while self.running:  # Server çalıştığı sürece yeni bağlantıları kabul etmeye devam eder.
            client_socket, client_address = self.server_socket.accept()  # Yeni client bağlantısını kabul eder.

            if len(self.clients) >= MAX_PLAYERS:  # Eğer maksimum oyuncu sayısına ulaşıldıysa kontrol eder.
                client_socket.sendall(  # Yeni bağlanan client'a hata mesajı gönderir.
                    encode_message({
                        "type": ERROR,  # Mesaj tipinin hata olduğunu belirtir.
                        "message": "Game is full."  # Oyunun dolu olduğunu açıklar.
                    })
                )
                client_socket.close()  # Fazladan client bağlantısını kapatır.
                continue  # Yeni bağlantı beklemeye devam eder.


            player_id = len(self.clients) + 1  # Yeni bağlanan oyuncuya oyuncu numarası verir.
            self.clients[player_id] = client_socket  # Oyuncunun socket bağlantısını clients sözlüğüne kaydeder.

            print(f"[SERVER] Player {player_id} connected from {client_address}")  # Bağlanan oyuncunun bilgisini konsola yazdırır.

            client_socket.sendall(  # Oyuncuya oyuncu numarasını gönderir.
                encode_message({
                    "type": ASSIGN_PLAYER,  # Mesaj tipinin oyuncu atama olduğunu belirtir.
                    "player_id": player_id  # Oyuncuya verilen ID bilgisini gönderir.
                })
            )


            if len(self.clients) < MAX_PLAYERS:  # Eğer henüz ikinci oyuncu bağlanmadıysa kontrol eder.
                client_socket.sendall(  # İlk oyuncuya bekleme mesajı gönderir.
                    encode_message({
                        "type": WAITING,  # Mesaj tipinin bekleme olduğunu belirtir.
                        "message": "Waiting for second player..."  # İkinci oyuncunun beklendiğini bildirir.
                    })
                )
            else:  # Eğer iki oyuncu da bağlandıysa çalışır.
                self.broadcast({  # Tüm oyunculara oyun başlangıç mesajı gönderir.
                    "type": GAME_START,  # Mesaj tipinin oyun başlangıcı olduğunu belirtir.
                    "message": "Both players connected. Game started!",  # Oyunun başladığını açıklar.
                    "state": self.game.get_state()  # Güncel oyun durumunu client'lara gönderir.
                })


            thread = Thread(target=self.handle_client, args=(player_id,))  # Her oyuncu için ayrı dinleme thread'i oluşturur.
            thread.daemon = True  # Ana program kapanınca thread'in de kapanmasını sağlar.
            thread.start()  # Oyuncu thread'ini başlatır.

    def handle_client(self, player_id):  # Belirli bir oyuncudan gelen mesajları dinler.
        client_socket = self.clients[player_id]  # Oyuncunun socket bağlantısını alır.
        buffer = ""  # Parçalı gelen mesajları biriktirmek için boş buffer oluşturur.

        while self.running:  # Server çalıştığı sürece mesaj dinlemeye devam eder.
            try:  # Veri alma sırasında oluşabilecek hataları yakalamak için try bloğu başlatır.
                data = client_socket.recv(1024)  # Client'tan maksimum 1024 byte veri alır.

                if not data:  # Veri gelmiyorsa bağlantının kapandığını anlar.
                    break  # Döngüden çıkar.

                buffer += data.decode("utf-8")  # Gelen byte verisini UTF-8 metne çevirip buffer'a ekler.

                while "\n" in buffer:  # Buffer içinde tam mesaj olduğu sürece çalışır.
                    line, buffer = buffer.split("\n", 1)  # İlk tam mesajı ayırır, kalan kısmı buffer'da bırakır.
                    message = decode_message(line)  # JSON mesajını Python dict tipine çevirir.
                    self.process_message(player_id, message)  # Gelen mesajı işleme metoduna gönderir.

            except ConnectionError:  # Bağlantı kopması durumunda çalışır.
                break  # Döngüden çıkar.
            except Exception as error:  # Diğer hatalar oluşursa çalışır.
                print(f"[SERVER] Error for Player {player_id}: {error}")  # Hata bilgisini konsola yazdırır.
                break  # Döngüden çıkar.

        self.remove_client(player_id)  # Oyuncu bağlantısı kapandığında oyuncuyu sistemden kaldırır.

    def process_message(self, player_id, message):  # Client'tan gelen mesajları türüne göre işler.
        message_type = message.get("type")  # Mesajın type alanını alır.

        if message_type == ROLL_DICE:  # Eğer oyuncu zar atmak istediyse çalışır.
            result = self.game.roll_for_player(player_id)  # GameLogic üzerinden zar atma işlemini gerçekleştirir.

            if not result["success"]:  # Eğer işlem başarısız olduysa kontrol eder.
                self.send_to_player(player_id, {  # Sadece ilgili oyuncuya hata mesajı gönderir.
                    "type": ERROR,  # Mesaj tipinin hata olduğunu belirtir.
                    "message": result["message"]  # Hata açıklamasını gönderir.
                })
                return  # Fonksiyondan çıkar.

            state = self.game.get_state()  # Güncel oyun durumunu alır.

            self.broadcast({  # Tüm oyunculara güncel oyun durumunu gönderir.
                "type": GAME_STATE,  # Mesaj tipinin oyun durumu olduğunu belirtir.
                "state": state  # Güncel oyun durumunu gönderir.
            })

            if state["game_over"]:  # Oyun bittiyse kontrol eder.
                self.broadcast({  # Tüm oyunculara oyun bitti mesajı gönderir.
                    "type": GAME_OVER,  # Mesaj tipinin oyun sonu olduğunu belirtir.
                    "winner": state["winner"],  # Kazanan oyuncu bilgisini gönderir.
                    "state": state  # Son oyun durumunu gönderir.
                })


        elif message_type == RESTART_REQUEST:  # Eğer oyuncu tekrar oynama isteği gönderdiyse çalışır.

            if not self.game.game_over:  # Oyun bitmeden tekrar oynama isteği geldiyse kontrol eder.
                self.send_to_player(player_id, {  # Oyuncuya hata mesajı gönderir.

                    "type": ERROR,  # Mesaj tipinin hata olduğunu belirtir.

                    "message": "Game is not over yet."  # Oyunun henüz bitmediğini açıklar.

                })

                return  # Fonksiyondan çıkar.

            self.restart_votes.add(player_id)  # Tekrar oynamak isteyen oyuncuyu restart_votes kümesine ekler.

            if len(self.restart_votes) < MAX_PLAYERS:  # Tüm oyuncular tekrar oynama istemediyse kontrol eder.
                self.broadcast({  # Oyunculara bekleme mesajı gönderir.

                    "type": RESTART_WAITING,  # Mesaj tipinin tekrar oynama bekleme olduğunu belirtir.

                    "message": f"Player {player_id} wants to play again. Waiting for other player..."  # Diğer oyuncunun beklendiğini açıklar.

                })

                return  # Fonksiyondan çıkar.

            self.restart_votes.clear()  # Tüm oyuncular kabul ettiği için oy yeniden başlatma oylarını temizler.

            self.game.reset_game()  # Oyun durumunu sıfırlar.

            self.broadcast({  # Tüm oyunculara yeni oyunun başladığını bildirir.

                "type": GAME_START,  # Mesaj tipinin oyun başlangıcı olduğunu belirtir.

                "message": "Both players accepted. New game started!",  # Yeni oyunun başladığını açıklar.

                "state": self.game.get_state()  # Sıfırlanmış oyun durumunu gönderir.

            })

    def send_to_player(self, player_id, message):  # Belirli bir oyuncuya mesaj gönderir.
        if player_id in self.clients:  # Oyuncu hâlâ bağlıysa kontrol eder.
            self.clients[player_id].sendall(encode_message(message))  # Mesajı JSON byte formatında oyuncuya gönderir.

    def broadcast(self, message):  # Tüm bağlı oyunculara aynı mesajı gönderir.
        for client_socket in self.clients.values():  # Tüm oyuncu socket bağlantılarını dolaşır.
            client_socket.sendall(encode_message(message))  # Mesajı her oyuncuya gönderir.

    def remove_client(self, player_id):  # Oyuncu bağlantısı kesildiğinde oyuncuyu sistemden kaldırır.
        print(f"[SERVER] Player {player_id} disconnected.")  # Ayrılan oyuncu bilgisini konsola yazdırır.

        if player_id in self.clients:  # Oyuncu hâlâ clients sözlüğünde varsa kontrol eder.
            try:  # Socket kapatılırken oluşabilecek hataları yakalamak için try bloğu başlatır.
                self.clients[player_id].close()  # Oyuncunun socket bağlantısını kapatır.
            except Exception:  # Socket kapanırken hata oluşursa çalışır.
                pass  # Hatayı yok sayar.

            del self.clients[player_id]  # Oyuncuyu clients sözlüğünden siler.

        self.restart_votes.discard(player_id)  # Oyuncu tekrar oynama listesinde varsa kaldırır.

        if len(self.clients) == 0:  # Hiç oyuncu kalmadıysa kontrol eder.
            print("[SERVER] All players disconnected. Game reset.")  # Konsola oyun sıfırlandı mesajı yazdırır.
            self.game.reset_game()  # Oyunu başlangıç durumuna döndürür.
            self.restart_votes.clear()  # Tekrar oynama oylarını temizler.
            return  # Fonksiyondan çıkar.

        self.broadcast({  # Kalan oyunculara rakibin ayrıldığını bildirir.
            "type": OPPONENT_LEFT,  # Mesaj tipinin rakip ayrıldı olduğunu belirtir.
            "message": f"Player {player_id} left the game."  # Ayrılan oyuncu bilgisini gönderir.
        })


if __name__ == "__main__":  # Bu dosya doğrudan çalıştırıldığında aşağıdaki kodların çalışmasını sağlar.
    server = GameServer()  # GameServer nesnesi oluşturur.
    server.start()  # Server'ı başlatır.