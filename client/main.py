import os  # Dosya ve klasör yollarıyla işlem yapmak için os modülünü içe aktarır.
import sys  # Python çalışma ortamı ve sistem yolu işlemleri için sys modülünü içe aktarır.

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Bu dosyanın bulunduğu client klasörünün tam yolunu alır.
PROJECT_DIR = os.path.dirname(CURRENT_DIR)  # Client klasörünün bir üst klasörünü, yani proje ana klasörünü alır.

if PROJECT_DIR not in sys.path:  # Proje ana klasörü Python import yolları arasında yoksa kontrol eder.
    sys.path.insert(0, PROJECT_DIR)  # Proje ana klasörünü import yollarına ekler.

from PyQt6.QtWidgets import QApplication, QMessageBox  # PyQt uygulaması ve mesaj kutusu sınıflarını içe aktarır.

from client.start_window import StartWindow  # Başlangıç ekranı sınıfını içe aktarır.
from client.game_window import GameWindow  # Oyun ekranı sınıfını içe aktarır.
from client.network import NetworkClient  # Server ile iletişimi yöneten network client sınıfını içe aktarır.
from client.result_dialog import ResultDialog  # Oyun bitince gösterilen sonuç penceresini içe aktarır.

from common.protocol import (  # Client ve server arasında kullanılan mesaj tiplerini içe aktarır.
    ASSIGN_PLAYER,  # Server'ın client'a oyuncu numarası atadığını belirten mesaj tipidir.
    WAITING,  # İkinci oyuncu beklenirken gelen mesaj tipidir.
    GAME_START,  # Oyunun başladığını veya yeniden başladığını belirten mesaj tipidir.
    GAME_STATE,  # Güncel oyun durumunu taşıyan mesaj tipidir.
    GAME_OVER,  # Oyunun bittiğini belirten mesaj tipidir.
    ERROR,  # Hata mesajlarını belirten mesaj tipidir.
    RESTART_REQUEST,  # Client'ın tekrar oynama isteğini belirten mesaj tipidir.
    OPPONENT_LEFT,  # Rakibin oyundan ayrıldığını belirten mesaj tipidir.
    RESTART_WAITING,  # Diğer oyuncunun tekrar oynama onayının beklendiğini belirten mesaj tipidir.
)


class ClientApp:  # Client uygulamasının tüm ekranlarını ve network bağlantısını yöneten ana sınıftır.
    def __init__(self):  # ClientApp nesnesi oluşturulduğunda çalışan kurucu metottur.
        self.app = QApplication(sys.argv)  # PyQt uygulama nesnesini oluşturur.

        self.network_client = NetworkClient()  # Server ile bağlantı kuracak network client nesnesini oluşturur.

        self.start_window = StartWindow(self.connect_to_server)  # Başlangıç ekranını oluşturur ve bağlanma fonksiyonunu gönderir.
        self.game_window = GameWindow(self.network_client)  # Oyun ekranını oluşturur ve network client nesnesini verir.

        self.player_id = None  # Bu client'a atanacak oyuncu numarasını başlangıçta boş tutar.
        self.result_dialog = None  # Oyun bitiş penceresini başlangıçta boş tutar.

        self.network_client.connection_success.connect(self.connection_success)  # Bağlantı başarılı olunca çalışacak metodu bağlar.
        self.network_client.connection_error.connect(self.connection_error)  # Bağlantı hatası olunca çalışacak metodu bağlar.
        self.network_client.message_received.connect(self.handle_server_message)  # Server'dan mesaj gelince çalışacak metodu bağlar.

    def run(self):  # Client uygulamasını başlatır.
        self.start_window.show()  # İlk olarak başlangıç ekranını gösterir.
        sys.exit(self.app.exec())  # PyQt olay döngüsünü başlatır ve uygulama kapanınca programdan çıkar.

    def connect_to_server(self, server_ip, server_port):  # Başlangıç ekranından gelen IP ve port ile server'a bağlanır.
        self.network_client.connect_to_server(server_ip, server_port)  # NetworkClient üzerinden server bağlantısını başlatır.

    def connection_success(self):  # Server bağlantısı başarılı olunca çalışır.
        self.start_window.hide()  # Başlangıç ekranını gizler.
        self.game_window.show()  # Oyun ekranını gösterir.

    def connection_error(self, error_message):  # Server bağlantısı sırasında hata olursa çalışır.
        QMessageBox.critical(  # Kullanıcıya kritik hata mesaj kutusu gösterir.
            self.start_window,  # Mesaj kutusunun başlangıç ekranı üzerinde görünmesini sağlar.
            "Connection Error",  # Mesaj kutusunun başlığını belirler.
            error_message  # Gösterilecek hata mesajını belirler.
        )

        self.start_window.reset_button()  # Başlangıç ekranındaki connect butonunu tekrar aktif hale getirir.

    def handle_server_message(self, message):  # Server'dan gelen tüm mesajları türüne göre işler.
        message_type = message.get("type")  # Gelen mesajın type alanını alır.

        if message_type == ASSIGN_PLAYER:  # Eğer server oyuncu numarası atadıysa çalışır.
            self.player_id = message.get("player_id")  # Mesajdan oyuncu numarasını alır.
            self.game_window.set_player_id(self.player_id)  # Oyun ekranında oyuncu numarasını gösterir.

        elif message_type == WAITING:  # Eğer ikinci oyuncu bekleniyorsa çalışır.
            self.game_window.add_message(message.get("message", "Waiting..."))  # Bekleme mesajını oyun ekranına yazar.

        elif message_type == GAME_START:  # Eğer oyun başlatıldıysa veya yeniden başlatıldıysa çalışır.
            self.game_window.add_message(message.get("message", "Game started."))  # Oyun başlangıç mesajını ekrana yazar.

            state = message.get("state")  # Mesaj içindeki güncel oyun durumunu alır.
            if state:  # Eğer oyun durumu geldiyse kontrol eder.
                self.game_window.update_game_state(state)  # Oyun ekranını gelen duruma göre günceller.

        elif message_type == GAME_STATE:  # Eğer server güncel oyun durumunu gönderdiyse çalışır.
            state = message.get("state")  # Mesaj içindeki oyun durumunu alır.
            if state:  # Eğer state bilgisi varsa kontrol eder.
                self.game_window.update_game_state(state)  # Tahta, sıra, zar ve mesaj bilgilerini günceller.


        elif message_type == GAME_OVER:  # Eğer oyun bittiyse çalışır.
            state = message.get("state")  # Oyun bitiş anındaki son oyun durumunu alır.
            winner = message.get("winner")  # Kazanan oyuncu numarasını alır.

            if state:  # Eğer son oyun durumu geldiyse kontrol eder.
                self.game_window.update_game_state(state)  # Oyun ekranını son durumla günceller.

            self.show_result_dialog(winner)  # Kazanan bilgisine göre bitiş penceresini gösterir.


        elif message_type == RESTART_WAITING:  # Eğer bir oyuncu tekrar oynamak istedi ve diğer oyuncu bekleniyorsa çalışır.
            self.game_window.add_message(  # Bekleme bilgisini oyun mesaj kutusuna ekler.
                message.get("message", "Waiting for other player to play again...")  # Server mesajını alır, yoksa varsayılan mesajı kullanır.
            )


        elif message_type == ERROR:  # Eğer server hata mesajı gönderdiyse çalışır.
            QMessageBox.warning(  # Kullanıcıya uyarı mesaj kutusu gösterir.
                self.game_window,  # Mesaj kutusunun oyun ekranı üzerinde görünmesini sağlar.
                "Game Error",  # Uyarı penceresinin başlığını belirler.
                message.get("message", "Unknown error.")  # Hata mesajını alır, yoksa varsayılan hata mesajını gösterir.
            )

        elif message_type == OPPONENT_LEFT:  # Eğer rakip oyuncu oyundan ayrıldıysa çalışır.
            QMessageBox.warning(  # Kullanıcıya rakibin ayrıldığını bildiren uyarı gösterir.
                self.game_window,  # Mesaj kutusunun oyun ekranı üzerinde görünmesini sağlar.
                "Opponent Left",  # Uyarı penceresinin başlığını belirler.
                message.get("message", "Opponent left the game.")  # Server mesajını alır, yoksa varsayılan mesajı gösterir.
            )

    def show_result_dialog(self, winner):  # Oyun bitiş penceresini gösterir.
        if self.result_dialog is not None:  # Eğer sonuç penceresi zaten açıksa kontrol eder.
            return  # Yeni pencere açmadan fonksiyondan çıkar.

        self.result_dialog = ResultDialog(  # Sonuç penceresi nesnesini oluşturur.
            winner=winner,  # Kazanan oyuncu numarasını pencereye gönderir.
            player_id=self.player_id,  # Bu client'ın oyuncu numarasını pencereye gönderir.
            on_restart=self.restart_game  # Tekrar oynama butonuna basıldığında çalışacak fonksiyonu gönderir.
        )

        self.result_dialog.exec()  # Sonuç penceresini modal olarak açar.
        self.result_dialog = None  # Pencere kapandıktan sonra değişkeni tekrar boşaltır.

    def restart_game(self):  # Tekrar oynama isteğini server'a gönderir.
        self.network_client.send_message({  # NetworkClient üzerinden server'a mesaj gönderir.
            "type": RESTART_REQUEST  # Mesaj tipinin tekrar oynama isteği olduğunu belirtir.
        })


if __name__ == "__main__":  # Bu dosya doğrudan çalıştırıldığında aşağıdaki kodların çalışmasını sağlar.
    client_app = ClientApp()  # ClientApp nesnesi oluşturur.
    client_app.run()  # Client uygulamasını başlatır.