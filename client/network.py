#bu kod bloğunun görevi servera bağlanmak(network), mesaj göndermke, mesaj dinlemek
#gelen mesajı main'e iletmek ve bağlantı koparsa haber vermek

# Socket ile sunucuya bağlanmak için gerekli modül.
import socket

# Mesaj dinleme işini ayrı thread'de yapmak için Thread kullanıyoruz.
from threading import Thread

# Tip ipucu için Optional kullanıyoruz.
from typing import Optional

# Protokoldeki yardımcı fonksiyonu ve sabitleri alıyoruz.
from common.protocol import decode_message, encode_message


# Bu sınıf istemcinin sunucu ile ağ iletişimini yönetecek.
class ClientNetwork:
    # Sınıf oluşturulurken callback fonksiyonlarını dışarıdan alıyoruz.
    def __init__(self, on_message_received=None, on_disconnected=None):
        # Sunucuyla konuşacağımız socket burada tutulacak.
        self.client_socket: Optional[socket.socket] = None

        # Mesaj dinleme thread'i burada tutulacak.
        self.listen_thread = None

        # İstemci bağlı mı bilgisini tutuyoruz.
        self.is_connected = False

        # Sunucudan mesaj geldiğinde çağrılacak fonksiyon.
        self.on_message_received = on_message_received

        # Bağlantı kopunca çağrılacak fonksiyon.
        self.on_disconnected = on_disconnected

    # Bu fonksiyon sunucuya bağlanır.
    def connect_to_server(self, server_ip, server_port):
        try:
            # TCP socket oluşturuyoruz.
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Verilen IP ve porta bağlanıyoruz.
            client_socket.connect((server_ip, server_port))

            # Socket'i sınıf değişkenine kaydediyoruz.
            self.client_socket = client_socket

            # Bağlantı kuruldu bilgisini tutuyoruz.
            self.is_connected = True

            # Sunucudan gelen mesajları dinlemek için ayrı thread başlatıyoruz.
            self.listen_thread = Thread(target=self.message_listen_thread)

            # Program kapanırken bu thread'in takılmaması için daemon yapıyoruz.
            self.listen_thread.daemon = True

            # Thread'i başlatıyoruz.
            self.listen_thread.start()

            # Bağlantı başarılı olduysa True döndürüyoruz.
            return True, "Connected successfully."

        except Exception as e:
            # Hata varsa bağlantı kurulamadı bilgisini döndürüyoruz.
            return False, str(e)

    # Bu fonksiyon sunucudan gelen mesajları sürekli dinler,veri gelirse decode eder, json dict çevirir.
    def message_listen_thread(self):
        # Socket varsa ve bağlantı aktifse döngü devam etsin.
        while self.client_socket and self.is_connected:
            try:
                # Sunucudan en fazla 1024 byte veri alıyoruz.
                message_bytes = self.client_socket.recv(1024)

            except ConnectionError:
                # Bağlantı hatası olursa kopma işlemini yapıyoruz.
                self.handle_disconnect()
                return

            except Exception:
                # Beklenmeyen hata olursa yine kopmuş gibi davranıyoruz.
                self.handle_disconnect()
                return

            # Eğer boş veri geldiyse bağlantı kapanmış olabilir.
            if not message_bytes:
                self.handle_disconnect()
                return

            try:
                # Gelen byte veriyi stringe çeviriyoruz.
                message_text = message_bytes.decode("utf-8").strip()

                # JSON metni dicte çeviriyoruz.
                data = decode_message(message_text)

            except Exception:
                # Mesaj bozuksa bu mesajı atlayıp dinlemeye devam ediyoruz.
                continue

            # Eğer mesaj geldiğinde çağrılacak fonksiyon tanımlıysa onu çağırıyoruz.
            if self.on_message_received:
                self.on_message_received(data)

    # Bu fonksiyon sunucuya mesaj gönderir.
    def send_message(self, message_dict):
        # Eğer bağlantı yoksa mesaj gönderemeyiz.
        if not self.client_socket or not self.is_connected:
            return False

        try:
            # Sözlüğü byte haline getirip sunucuya gönderiyoruz.
            self.client_socket.sendall(encode_message(message_dict))

            # Gönderim başarılı olduysa True döndürüyoruz.
            return True

        except Exception:
            # Hata varsa bağlantıyı düşürüp False döndürüyoruz.
            self.handle_disconnect()
            return False

    # Bu fonksiyon bağlantı kopunca çalışır.
    def handle_disconnect(self):
        # Artık bağlı değil bilgisini tutuyoruz.
        self.is_connected = False

        # Socket varsa kapatmayı deniyoruz.
        if self.client_socket:
            try:
                self.client_socket.close()
            except Exception:
                pass

        # Socket referansını temizliyoruz.
        self.client_socket = None

        # Dışarıya "bağlantı koptu" diye haber veriyoruz.
        if self.on_disconnected:
            self.on_disconnected()

    # Bu fonksiyon bağlantıyı elle kapatmak için kullanılır.
    def close_connection(self):
        # Bağlantı koparma işlemini ortak fonksiyonla yapıyoruz.
        self.handle_disconnect()