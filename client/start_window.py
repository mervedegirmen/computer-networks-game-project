from PyQt6.QtWidgets import (  # Başlangıç ekranında kullanılacak PyQt6 widget sınıflarını içe aktarır.
    QWidget,  # StartWindow sınıfının temel pencere/widget sınıfıdır.
    QVBoxLayout,  # Widget'ları dikey şekilde sıralamak için kullanılır.
    QLabel,  # Başlık ve açıklama yazıları için kullanılır.
    QLineEdit,  # IP adresi ve port giriş kutuları için kullanılır.
    QPushButton,  # Server'a bağlanma butonu için kullanılır.
    QMessageBox,  # Hata ve uyarı mesaj kutularını göstermek için kullanılır.
)
from PyQt6.QtCore import Qt  # Hizalama gibi Qt sabitlerini kullanmak için içe aktarılır.

from common.constants import DEFAULT_HOST, DEFAULT_PORT  # Varsayılan server IP adresi ve port numarasını içe aktarır.


class StartWindow(QWidget):  # Oyunun başlangıç ekranını temsil eden QWidget sınıfıdır.
    def __init__(self, on_connect):  # StartWindow oluşturulurken çalışır ve bağlantı fonksiyonunu parametre olarak alır.
        super().__init__()  # QWidget sınıfının kurucu metodunu çalıştırır.

        self.on_connect = on_connect  # Server bağlantısı yapılınca çağrılacak fonksiyonu saklar.

        self.setWindowTitle("Snakes and Ladders - Start")  # Başlangıç ekranının pencere başlığını ayarlar.
        self.setFixedSize(420, 300)  # Başlangıç ekranının boyutunu sabitler.

        layout = QVBoxLayout()  # Widget'ları dikey yerleştirecek layout oluşturur.
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Layout içindeki elemanları merkeze hizalar.
        layout.setSpacing(15)  # Widget'lar arasındaki boşluğu 15 piksel yapar.

        title_label = QLabel("Snakes and Ladders")  # Oyun başlığını gösterecek etiketi oluşturur.
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Başlık yazısını ortalar.
        title_label.setStyleSheet("font-size: 26px; font-weight: bold;")  # Başlık yazısının boyutunu ve kalınlığını ayarlar.

        subtitle_label = QLabel("Computer Networks Project")  # Alt açıklama yazısını gösterecek etiketi oluşturur.
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Alt başlığı ortalar.
        subtitle_label.setStyleSheet("font-size: 14px; color: gray;")  # Alt başlığın yazı boyutunu ve rengini ayarlar.

        self.ip_input = QLineEdit()  # Server IP adresinin girileceği giriş kutusunu oluşturur.
        self.ip_input.setPlaceholderText("Server IP Address")  # Giriş kutusu boşken gösterilecek açıklama yazısını ayarlar.
        self.ip_input.setText(DEFAULT_HOST)  # Varsayılan IP adresini giriş kutusuna yerleştirir.

        self.port_input = QLineEdit()  # Server port numarasının girileceği giriş kutusunu oluşturur.
        self.port_input.setPlaceholderText("Server Port")  # Port giriş kutusu boşken gösterilecek açıklama yazısını ayarlar.
        self.port_input.setText(str(DEFAULT_PORT))  # Varsayılan port numarasını giriş kutusuna yerleştirir.

        self.connect_button = QPushButton("Connect to Server")  # Server bağlantısı için buton oluşturur.
        self.connect_button.clicked.connect(self.connect_clicked)  # Butona basılınca connect_clicked metodunun çalışmasını sağlar.

        layout.addWidget(title_label)  # Başlık etiketini layout'a ekler.
        layout.addWidget(subtitle_label)  # Alt başlık etiketini layout'a ekler.
        layout.addWidget(self.ip_input)  # IP giriş kutusunu layout'a ekler.
        layout.addWidget(self.port_input)  # Port giriş kutusunu layout'a ekler.
        layout.addWidget(self.connect_button)  # Bağlanma butonunu layout'a ekler.

        self.setLayout(layout)  # Oluşturulan layout'u pencereye uygular.

    def connect_clicked(self):  # Kullanıcı connect butonuna bastığında çalışan metottur.
        server_ip = self.ip_input.text().strip()  # IP giriş kutusundaki metni alır ve baştaki/sondaki boşlukları temizler.
        port_text = self.port_input.text().strip()  # Port giriş kutusundaki metni alır ve boşlukları temizler.

        if not server_ip:  # Eğer IP adresi boş bırakıldıysa kontrol eder.
            QMessageBox.warning(self, "Input Error", "Please enter server IP address.")  # Kullanıcıya uyarı mesajı gösterir.
            return  # Fonksiyondan çıkar.

        if not port_text.isdigit():  # Eğer port değeri sadece rakamlardan oluşmuyorsa kontrol eder.
            QMessageBox.warning(self, "Input Error", "Port must be a number.")  # Kullanıcıya portun sayı olması gerektiğini bildirir.
            return  # Fonksiyondan çıkar.

        server_port = int(port_text)  # Port metnini integer veri tipine çevirir.

        self.connect_button.setEnabled(False)  # Kullanıcı tekrar tekrar basamasın diye butonu pasif yapar.
        self.connect_button.setText("Connecting...")  # Buton yazısını bağlantı kuruluyor olarak değiştirir.

        self.on_connect(server_ip, server_port)  # Girilen IP ve port bilgisiyle bağlantı fonksiyonunu çağırır.

    def reset_button(self):  # Bağlantı başarısız olursa connect butonunu eski haline getirir.
        self.connect_button.setEnabled(True)  # Connect butonunu tekrar aktif hale getirir.
        self.connect_button.setText("Connect to Server")  # Buton yazısını tekrar eski haline döndürür.