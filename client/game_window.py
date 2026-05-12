from PyQt6.QtCore import Qt  # Qt hizalama ve genel sabitlerini kullanmak için içe aktarılır.
from PyQt6.QtWidgets import (  # Arayüzde kullanılacak temel PyQt6 widget ve layout sınıfları içe aktarılır.
    QWidget,  # GameWindow sınıfının temel pencere/widget sınıfıdır.
    QVBoxLayout,  # Sağ panelde elemanları dikey sıralamak için kullanılır.
    QHBoxLayout,  # Ana ekranda tahta ve sağ paneli yatay yerleştirmek için kullanılır.
    QLabel,  # Oyuncu, sıra, zar ve başlık metinlerini göstermek için kullanılır.
    QPushButton,  # Zar atma butonu için kullanılır.
    QTextEdit,  # Oyun mesajlarını göstermek için kullanılır.
)

from client.board_widget import BoardWidget  # Oyun tahtasını çizen özel BoardWidget sınıfını içe aktarır.
from common.protocol import ROLL_DICE  # Server'a zar atma isteği göndermek için kullanılan mesaj tipini içe aktarır.
from client.dice_widget import DiceWidget  # Zar görselini ve animasyonunu çizen özel DiceWidget sınıfını içe aktarır.


class GameWindow(QWidget):  # Oyun ekranını temsil eden ana PyQt6 widget sınıfıdır.
    def __init__(self, network_client):  # GameWindow oluşturulduğunda çalışan kurucu metottur.
        super().__init__()  # QWidget sınıfının kurucu metodunu çalıştırır.

        self.network_client = network_client  # Server ile iletişim kuracak NetworkClient nesnesini saklar.
        self.player_id = None  # Bu client'ın oyuncu numarasını başlangıçta boş tutar.
        self.current_turn = None  # Sıranın hangi oyuncuda olduğunu başlangıçta boş tutar.
        self.game_over = False  # Oyunun bitip bitmediğini tutar; başlangıçta oyun bitmemiştir.

        self.setWindowTitle("Snakes and Ladders")  # Oyun penceresinin başlığını ayarlar.
        self.resize(950, 750)  # Oyun penceresinin başlangıç boyutunu ayarlar.

        main_layout = QHBoxLayout()  # Tahta ve sağ paneli yan yana koyacak ana yatay layout oluşturur.

        self.board = BoardWidget()  # Sol tarafta gösterilecek oyun tahtası widget'ını oluşturur.

        right_panel = QVBoxLayout()  # Sağ taraftaki bilgi ve kontrol paneli için dikey layout oluşturur.
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)  # Sağ paneldeki elemanları üst tarafa hizalar.
        right_panel.setSpacing(15)  # Sağ paneldeki elemanlar arasına 15 piksel boşluk koyar.

        self.title_label = QLabel("Snakes and Ladders")  # Sağ panelde gösterilecek oyun başlığı etiketini oluşturur.
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Başlığı yatayda ortalar.
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")  # Başlığın yazı boyutunu ve kalınlığını ayarlar.

        self.player_label = QLabel("Player: -")  # Oyuncu numarasını gösterecek etiketi oluşturur.
        self.player_label.setStyleSheet("font-size: 16px;")  # Oyuncu etiketi yazı boyutunu ayarlar.

        self.turn_label = QLabel("Turn: -")  # Sıranın hangi oyuncuda olduğunu gösterecek etiketi oluşturur.
        self.turn_label.setStyleSheet("font-size: 16px;")  # Sıra etiketi yazı boyutunu ayarlar.

        self.dice_label = QLabel("Dice: -")  # Son gelen zar değerini metin olarak gösterecek etiketi oluşturur.
        self.dice_label.setStyleSheet("font-size: 18px; font-weight: bold;")  # Zar etiketi yazı boyutunu ve kalınlığını ayarlar.
        self.dice_widget = DiceWidget()  # Zar yüzünü görsel olarak gösterecek DiceWidget nesnesini oluşturur.


        self.roll_button = QPushButton("Roll Dice")  # Zar atma butonunu oluşturur.
        self.roll_button.setFixedHeight(45)  # Zar atma butonunun yüksekliğini sabitler.
        self.roll_button.setEnabled(False)  # Oyun başlamadan veya sıra gelmeden butonu pasif yapar.
        self.roll_button.clicked.connect(self.roll_dice)  # Butona basıldığında roll_dice metodunun çalışmasını sağlar.

        self.message_box = QTextEdit()  # Oyun içi mesajların gösterileceği metin kutusunu oluşturur.
        self.message_box.setReadOnly(True)  # Kullanıcının mesaj kutusuna yazı yazmasını engeller.
        self.message_box.setMinimumHeight(250)  # Mesaj kutusunun minimum yüksekliğini ayarlar.

        right_panel.addWidget(self.title_label)  # Başlık etiketini sağ panele ekler.
        right_panel.addWidget(self.player_label)  # Oyuncu numarası etiketini sağ panele ekler.
        right_panel.addWidget(self.turn_label)  # Sıra bilgisini gösteren etiketi sağ panele ekler.
        right_panel.addWidget(self.dice_label)  # Zar değerini gösteren etiketi sağ panele ekler.
        right_panel.addWidget(self.dice_widget, alignment=Qt.AlignmentFlag.AlignCenter)  # Zar görselini sağ panelde ortalayarak ekler.
        right_panel.addWidget(self.roll_button)  # Zar atma butonunu sağ panele ekler.
        right_panel.addWidget(QLabel("Game Messages:"))  # Mesaj kutusunun başlığını sağ panele ekler.
        right_panel.addWidget(self.message_box)  # Oyun mesaj kutusunu sağ panele ekler.

        main_layout.addWidget(self.board, stretch=4)  # Oyun tahtasını ana layout'a ekler ve geniş alan kaplamasını sağlar.
        main_layout.addLayout(right_panel, stretch=1)  # Sağ bilgi panelini ana layout'a ekler ve daha dar alan kaplamasını sağlar.

        self.setLayout(main_layout)  # Oluşturulan ana layout'u GameWindow'a uygular.

    def set_player_id(self, player_id):  # Server tarafından atanan oyuncu numarasını arayüze işler.
        self.player_id = player_id  # Bu client'ın oyuncu numarasını kaydeder.
        self.player_label.setText(f"Player: {player_id}")  # Oyuncu etiketini günceller.
        self.add_message(f"You are Player {player_id}.")  # Mesaj kutusuna oyuncu numarasını bildirir.

    def update_game_state(self, state):  # Server'dan gelen güncel oyun durumunu arayüze uygular.
        positions = state.get("player_positions", {})  # Oyuncuların pozisyon bilgisini state içinden alır.
        self.current_turn = state.get("current_turn")  # Sıradaki oyuncu bilgisini state içinden alır.
        self.game_over = state.get("game_over", False)  # Oyunun bitip bitmediği bilgisini state içinden alır.

        self.board.update_board(positions)  # BoardWidget üzerindeki oyuncu pozisyonlarını günceller.

        self.turn_label.setText(f"Turn: Player {self.current_turn}")  # Sıra bilgisini ekranda günceller.

        last_roll = state.get("last_roll")  # Son zar değerini state içinden alır.
        if last_roll is not None:  # Son zar değeri varsa ekrandaki zar bilgisini günceller.
            self.dice_label.setText(f"Dice: {last_roll}")  # Zar değerini metin olarak gösterir.
            self.dice_widget.set_final_value(last_roll)  # Zar görselinin server'dan gelen gerçek değeri göstermesini sağlar.

        last_message = state.get("last_message")  # Server'dan gelen son oyun mesajını alır.
        if last_message:  # Son mesaj boş değilse mesaj kutusuna ekler.
            self.add_message(last_message)  # Oyun mesajını mesaj kutusuna yazar.

        self.update_roll_button()  # Sıra ve oyun durumuna göre zar butonunu günceller.

    def update_roll_button(self):  # Oyuncunun zar atıp atamayacağını kontrol ederek buton durumunu günceller.
        if self.game_over:  # Oyun bitmişse zar butonu kapatılır.
            self.roll_button.setEnabled(False)  # Zar butonunu pasif hale getirir.
            self.roll_button.setText("Game Over")  # Buton yazısını oyun bitti olarak değiştirir.
            return  # Fonksiyondan çıkar.

        if self.player_id == self.current_turn:  # Eğer sıra bu client'ın oyuncusundaysa buton aktif olur.
            self.roll_button.setEnabled(True)  # Zar butonunu aktif hale getirir.
            self.roll_button.setText("Roll Dice")  # Buton yazısını zar atma olarak ayarlar.
        else:  # Eğer sıra rakip oyuncudaysa buton pasif olur.
            self.roll_button.setEnabled(False)  # Zar butonunu pasif hale getirir.
            self.roll_button.setText("Opponent's Turn")  # Buton yazısını rakibin sırası olarak ayarlar.

    def roll_dice(self):  # Zar butonuna basıldığında server'a zar atma isteği gönderir.
        self.roll_button.setEnabled(False)  # Aynı anda tekrar basılmasını önlemek için butonu geçici olarak pasif yapar.

        self.network_client.send_message({  # NetworkClient üzerinden server'a mesaj gönderir.
            "type": ROLL_DICE  # Mesaj tipinin zar atma isteği olduğunu belirtir.
        })

    def add_message(self, message):  # Oyun mesajlarını mesaj kutusuna ekler.
        self.message_box.append(message)  # Gelen mesajı QTextEdit içine yeni satır olarak ekler.