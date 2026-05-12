from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton  # Sonuç penceresi, dikey layout, yazı etiketi ve buton sınıflarını içe aktarır.
from PyQt6.QtCore import Qt  # Hizalama gibi Qt sabitlerini kullanmak için Qt sınıfını içe aktarır.


class ResultDialog(QDialog):  # Oyun bitince gösterilecek sonuç penceresini temsil eden QDialog sınıfıdır.
    def __init__(self, winner, player_id, on_restart):  # Kazanan, mevcut oyuncu ve tekrar oynama fonksiyonu ile pencereyi başlatır.
        super().__init__()  # QDialog sınıfının kurucu metodunu çalıştırır.

        self.on_restart = on_restart  # Tekrar oynama butonuna basılınca çalışacak fonksiyonu saklar.

        self.setWindowTitle("Game Over")  # Sonuç penceresinin başlığını ayarlar.
        self.setFixedSize(350, 220)  # Sonuç penceresinin boyutunu sabitler.

        layout = QVBoxLayout()  # Pencere içindeki elemanları dikey sıralamak için layout oluşturur.
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Layout içindeki elemanları merkeze hizalar.
        layout.setSpacing(20)  # Elemanlar arasındaki boşluğu 20 piksel yapar.

        if winner == player_id:  # Eğer kazanan oyuncu bu client'ın oyuncusuysa kontrol eder.
            result_text = "You Win!"  # Kullanıcı kazandıysa gösterilecek metni belirler.
        else:  # Eğer kazanan bu client değilse çalışır.
            result_text = "You Lose!"  # Kullanıcı kaybettiyse gösterilecek metni belirler.

        title_label = QLabel(result_text)  # Kazanma veya kaybetme sonucunu gösteren başlık etiketi oluşturur.
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Sonuç yazısını ortalar.
        title_label.setStyleSheet("font-size: 28px; font-weight: bold;")  # Sonuç yazısını büyük ve kalın yapar.

        winner_label = QLabel(f"Winner: Player {winner}")  # Kazanan oyuncu numarasını gösteren etiketi oluşturur.
        winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Kazanan yazısını ortalar.
        winner_label.setStyleSheet("font-size: 16px;")  # Kazanan yazısının boyutunu ayarlar.

        restart_button = QPushButton("Request Play Again")  # Tekrar oynama isteği gönderen butonu oluşturur.
        restart_button.setFixedHeight(40)  # Butonun yüksekliğini sabitler.
        restart_button.clicked.connect(self.restart_clicked)  # Butona basıldığında restart_clicked metodunu çalıştırır.

        layout.addWidget(title_label)  # Sonuç başlığını layout'a ekler.
        layout.addWidget(winner_label)  # Kazanan bilgisini layout'a ekler.
        layout.addWidget(restart_button)  # Tekrar oynama butonunu layout'a ekler.

        self.setLayout(layout)  # Oluşturulan layout'u sonuç penceresine uygular.

    def restart_clicked(self):  # Tekrar oynama butonuna basıldığında çalışan metottur.
        self.on_restart()  # Client tarafında server'a tekrar oynama isteği gönderen fonksiyonu çağırır.
        self.close()  # Sonuç penceresini kapatır.