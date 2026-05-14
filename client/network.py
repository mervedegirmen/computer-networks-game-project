import socket  # TCP/IP soket bağlantısı kurmak için socket modülünü içe aktarır.
from threading import Thread  # Server dinleme işlemini arayüzü dondurmadan ayrı thread'de çalıştırmak için Thread sınıfını içe aktarır.

from PyQt6.QtCore import QObject, pyqtSignal  # PyQt sinyal mekanizması için QObject ve pyqtSignal sınıflarını içe aktarır.

from common.protocol import encode_message, decode_message  # Mesajları JSON formatına çevirme ve JSON'dan çözme fonksiyonlarını içe aktarır.


class NetworkClient(QObject):  # Client tarafındaki ağ bağlantısını yöneten PyQt QObject sınıfıdır.
    message_received = pyqtSignal(dict)  # Server'dan mesaj gelince dict tipinde mesajı arayüze ileten sinyaldir.
    connection_success = pyqtSignal()  # Server bağlantısı başarılı olunca tetiklenen sinyaldir.
    connection_error = pyqtSignal(str)  # Bağlantı hatası oluşunca hata mesajını taşıyan sinyaldir.

    def __init__(self):  # NetworkClient nesnesi oluşturulduğunda çalışan kurucu metottur.
        super().__init__()  # QObject sınıfının kurucu metodunu çalıştırır.
        self.client_socket = None  # Server ile haberleşmek için kullanılacak client socket nesnesini başlangıçta boş tutar.
        self.listen_thread = None  # Server'dan gelen mesajları dinleyecek thread nesnesini başlangıçta boş tutar.
        self.running = False  # Dinleme döngüsünün çalışıp çalışmadığını kontrol eden değişkendir.

    def connect_to_server(self, server_ip, server_port):  # Verilen IP ve port ile server'a bağlanmayı dener.
        try:  # Bağlantı sırasında oluşabilecek hataları yakalamak için try bloğu başlatır.
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4 ve TCP kullanan socket nesnesi oluşturur.
            self.client_socket.connect((server_ip, server_port))  # Girilen server IP ve port bilgisiyle bağlantı kurar.

            self.running = True  # Bağlantı başarılı olduğu için dinleme döngüsünü aktif hale getirir.
            self.connection_success.emit()  # Arayüze bağlantının başarılı olduğunu bildiren sinyali gönderir.

            self.listen_thread = Thread(target=self.listen_server)  # Server mesajlarını dinleyecek thread'i oluşturur.
            self.listen_thread.daemon = True  # Ana program kapanınca bu thread'in de kapanmasını sağlar.
            self.listen_thread.start()  # Server dinleme thread'ini başlatır.

        except Exception as error:  # Bağlantı sırasında herhangi bir hata oluşursa çalışır.
            self.connection_error.emit(str(error))  # Hata mesajını arayüze sinyal olarak gönderir.

    def listen_server(self):  # Server'dan gelen mesajları sürekli dinleyen metottur.
        buffer = ""  # Parça parça gelen mesajları biriktirmek için boş metin tamponu oluşturur.

        while self.running and self.client_socket:  # Client çalıştığı ve socket açık olduğu sürece dinlemeye devam eder.
            try:  # Mesaj alma sırasında oluşabilecek hataları yakalamak için try bloğu başlatır.
                data = self.client_socket.recv(1024)  # Server'dan en fazla 1024 byte veri okur.

                if not data:  # Eğer veri gelmezse bağlantının kapandığını anlar.
                    self.connection_error.emit("Server connection closed.")  # Arayüze server bağlantısının kapandığını bildirir.
                    self.close_connection()  # Socket bağlantısını kapatır.
                    return  # Dinleme metodundan çıkar.

                buffer += data.decode("utf-8")  # Gelen byte verisini UTF-8 metne çevirip buffer'a ekler.

                while "\n" in buffer:  # Buffer içinde tam mesajı belirten satır sonu olduğu sürece çalışır.
                    line, buffer = buffer.split("\n", 1)  # İlk tam mesajı ayırır, kalan veriyi tekrar buffer'da tutar.

                    if line.strip():  # Mesaj satırı boş değilse kontrol eder.
                        message = decode_message(line)  # JSON metnini Python sözlüğüne çevirir.
                        self.message_received.emit(message)  # Gelen mesajı arayüze sinyal olarak gönderir.

            except Exception as error:  # Dinleme sırasında hata oluşursa çalışır.
                self.connection_error.emit(str(error))  # Hata mesajını arayüze sinyal olarak gönderir.
                self.close_connection()  # Bağlantıyı kapatır.
                return  # Dinleme metodundan çıkar.

    def send_message(self, message):  # Server'a mesaj göndermek için kullanılan metottur.
        if self.client_socket:  # Socket bağlantısı varsa mesaj göndermeye devam eder.
            try:  # Mesaj gönderme sırasında oluşabilecek hataları yakalamak için try bloğu başlatır.
                self.client_socket.sendall(encode_message(message))  # Mesajı JSON+newline formatına çevirip server'a gönderir.
            except Exception as error:  # Mesaj gönderirken hata oluşursa çalışır.
                self.connection_error.emit(str(error))  # Hata mesajını arayüze sinyal olarak gönderir.

    def close_connection(self):  # Client socket bağlantısını kapatır.
        self.running = False  # Dinleme döngüsünü durdurur.

        if self.client_socket:  # Eğer açık bir socket varsa kontrol eder.
            try:  # Socket kapatılırken oluşabilecek hataları yakalamak için try bloğu başlatır.
                self.client_socket.close()  # Socket bağlantısını kapatır.
            except Exception:  # Kapatma sırasında hata oluşursa çalışır.
                pass  # Hatayı yok sayar çünkü bağlantı zaten kapanma aşamasındadır.

            self.client_socket = None  # Socket değişkenini boşaltır.