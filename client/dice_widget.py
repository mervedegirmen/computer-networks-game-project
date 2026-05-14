import random  # Zar animasyonu sırasında rastgele 1-6 arası değer üretmek için kullanılır.

from PyQt6.QtCore import Qt, QTimer  # Qt sabitleri ve zamanlayıcı sınıfı içe aktarılır.
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QFont  # Çizim, fırça, kalem, renk ve font sınıfları içe aktarılır.
from PyQt6.QtWidgets import QWidget  # Özel zar widget'ı oluşturmak için QWidget sınıfı içe aktarılır.


class DiceWidget(QWidget):  # Zarın görsel olarak çizildiği özel QWidget sınıfıdır.
    def __init__(self):  # DiceWidget nesnesi oluşturulduğunda çalışan kurucu metottur.
        super().__init__()  # QWidget sınıfının kurucu metodunu çalıştırır.

        self.value = 1  # Ekranda o anda gösterilen zar değerini tutar.
        self.final_value = 1  # Animasyon bittikten sonra gösterilecek gerçek zar değerini tutar.
        self.animation_counter = 0  # Animasyonun kaç adım süreceğini takip eder.

        self.timer = QTimer()  # Zar animasyonunu belirli aralıklarla çalıştırmak için zamanlayıcı oluşturur.
        self.timer.timeout.connect(self.animate)  # Zamanlayıcı her tetiklendiğinde animate metodunu çağırır.

        self.setFixedSize(90, 90)  # Zar widget'ının genişlik ve yüksekliğini sabitler.

    def roll_animation(self):  # Zar atma animasyonunu başlatır.
        self.animation_counter = 12  # Animasyonun 12 kez rastgele zar yüzü göstermesini sağlar.
        self.timer.start(80)  # Zamanlayıcıyı 80 ms aralıklarla çalıştırır.

    def set_final_value(self, value):  # Server'dan gelen gerçek zar değerini ayarlar.
        self.final_value = value  # Animasyon sonunda gösterilecek değeri kaydeder.

        if not self.timer.isActive():  # Eğer animasyon şu anda çalışmıyorsa kontrol eder.
            self.value = value  # Zar yüzünü doğrudan gelen gerçek değere ayarlar.
            self.update()  # Widget'ın yeniden çizilmesini sağlar.

    def animate(self):  # Zar animasyonunun her adımında çalışan metottur.
        if self.animation_counter > 0:  # Animasyon adımı kaldıysa devam eder.
            self.value = random.randint(1, 6)  # Geçici olarak rastgele bir zar değeri gösterir.
            self.animation_counter -= 1  # Kalan animasyon adım sayısını bir azaltır.
            self.update()  # Zar widget'ını yeni değerle yeniden çizer.
        else:  # Animasyon adımları bittiyse çalışır.
            self.timer.stop()  # Zamanlayıcıyı durdurur.
            self.value = self.final_value  # Zar yüzünü server'dan gelen gerçek son değere ayarlar.
            self.update()  # Son değerin ekranda görünmesi için widget'ı yeniden çizer.

    def paintEvent(self, event):  # Widget ekrana çizilirken otomatik çalışan çizim metodudur.
        painter = QPainter(self)  # Bu widget üzerine çizim yapacak QPainter nesnesi oluşturur.
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Çizimlerin daha yumuşak ve düzgün görünmesini sağlar.

        painter.setBrush(QBrush(QColor(255, 245, 210)))  # Zarın iç dolgu rengini açık sarı olarak ayarlar.
        painter.setPen(QPen(QColor(180, 130, 40), 4))  # Zar kenarlığı için kahverengi kalem ve kalınlık ayarlar.
        painter.drawRoundedRect(5, 5, 80, 80, 12, 12)  # Yuvarlatılmış köşeli zar gövdesini çizer.

        painter.setBrush(QBrush(QColor(20, 20, 20)))  # Zar noktaları için siyah renge yakın dolgu ayarlar.
        painter.setPen(Qt.PenStyle.NoPen)  # Noktaların kenarlığı olmaması için kalemi kapatır.

        dot_positions = self.get_dot_positions(self.value)  # Mevcut zar değerine göre nokta koordinatlarını alır.

        for x, y in dot_positions:  # Zar üzerindeki her nokta koordinatını dolaşır.
            painter.drawEllipse(x, y, 10, 10)  # Zar noktasını küçük siyah daire olarak çizer.

        painter.setPen(QPen(QColor(80, 60, 20)))  # Sonraki çizimler için koyu kahverengi kalem ayarlar.
        font = QFont()  # Font nesnesi oluşturur.
        font.setPointSize(8)  # Font boyutunu ayarlar.
        font.setBold(True)  # Fontu kalın yapar.
        painter.setFont(font)  # Painter'a fontu uygular.

    def get_dot_positions(self, value):  # Zar değerine göre çizilecek noktaların koordinatlarını döndürür.
        positions = {  # Her zar değeri için nokta konumlarını tutan sözlüktür.
            1: [(40, 40)],  # 1 değeri için ortada tek nokta çizer.
            2: [(25, 25), (55, 55)],  # 2 değeri için çapraz iki nokta çizer.
            3: [(25, 25), (40, 40), (55, 55)],  # 3 değeri için çapraz üç nokta çizer.
            4: [(25, 25), (55, 25), (25, 55), (55, 55)],  # 4 değeri için dört köşede nokta çizer.
            5: [(25, 25), (55, 25), (40, 40), (25, 55), (55, 55)],  # 5 değeri için dört köşe ve orta nokta çizer.
            6: [(25, 22), (55, 22), (25, 40), (55, 40), (25, 58), (55, 58)],  # 6 değeri için iki sütunda altı nokta çizer.
        }

        return positions.get(value, positions[1])  # Geçerli değer yoksa varsayılan olarak 1 değerinin noktalarını döndürür.