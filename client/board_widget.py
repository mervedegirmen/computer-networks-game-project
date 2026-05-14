from PyQt6.QtCore import Qt, QPointF  # Qt sabitlerini ve 2D nokta sınıfını içe aktarır.
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont  # Çizim, renk, kalem, fırça ve font sınıflarını içe aktarır.
from PyQt6.QtWidgets import QWidget  # Özel çizim yapılacak QWidget sınıfını içe aktarır.

from common.constants import BOARD_SIZE, FINAL_SQUARE, SNAKES, LADDERS  # Tahta boyutu, son kare, yılanlar ve merdivenler sabitlerini alır.


class BoardWidget(QWidget):  # Oyun tahtasını çizen özel QWidget sınıfıdır.
    def __init__(self):  # BoardWidget nesnesi oluşturulduğunda çalışan kurucu metottur.
        super().__init__()  # QWidget sınıfının kurucu metodunu çalıştırır.

        self.player_positions = {  # Oyuncuların tahta üzerindeki başlangıç pozisyonlarını tutar.
            1: 0,  # 1. oyuncu başlangıçta tahtada değildir, pozisyonu 0’dır.
            2: 0,  # 2. oyuncu başlangıçta tahtada değildir, pozisyonu 0’dır.
        }

        self.snakes = SNAKES  # Yılanların başlangıç ve bitiş karelerini sınıf değişkenine atar.
        self.ladders = LADDERS  # Merdivenlerin başlangıç ve bitiş karelerini sınıf değişkenine atar.

        self.setMinimumSize(620, 620)  # Tahta widget’ının minimum boyutunu belirler.

    def update_board(self, player_positions):  # Oyuncu pozisyonları değiştiğinde tahtayı günceller.
        self.player_positions = {  # Sunucudan gelen oyuncu pozisyonlarını sözlük olarak yeniden oluşturur.
            int(player): position  # Oyuncu anahtarını integer’a çevirir ve pozisyonunu saklar.
            for player, position in player_positions.items()  # Gelen tüm oyuncu-pozisyon çiftleri üzerinde döner.
        }
        self.update()  # paintEvent metodunun yeniden çalışmasını sağlayarak tahtayı tekrar çizer.

    def paintEvent(self, event):  # QWidget ekrana çizilirken otomatik çalışan çizim metodudur.
        painter = QPainter(self)  # Bu widget üzerine çizim yapacak QPainter nesnesi oluşturur.
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Çizimlerin daha yumuşak görünmesini sağlar.

        board_size = min(self.width(), self.height()) - 40  # Widget boyutuna göre kare tahtanın toplam boyutunu hesaplar.
        cell_size = board_size / BOARD_SIZE  # Her bir karenin genişlik/yükseklik ölçüsünü hesaplar.

        start_x = (self.width() - board_size) / 2  # Tahtanın yatayda ortalanması için başlangıç x koordinatını hesaplar.
        start_y = (self.height() - board_size) / 2  # Tahtanın dikeyde ortalanması için başlangıç y koordinatını hesaplar.

        self.draw_cells(painter, start_x, start_y, cell_size)  # Tahta karelerini ve sayılarını çizer.
        self.draw_ladders(painter, start_x, start_y, cell_size)  # Merdivenleri çizer.
        self.draw_snakes(painter, start_x, start_y, cell_size)  # Yılanları çizer.
        self.draw_players(painter, start_x, start_y, cell_size)  # Oyuncu piyonlarını çizer.

    def draw_cells(self, painter, start_x, start_y, cell_size):  # Tahtadaki 100 kareyi ve kare numaralarını çizer.
        font = QFont()  # Kare numaraları için font nesnesi oluşturur.
        font.setPointSize(9)  # Yazı boyutunu ayarlar.
        font.setBold(True)  # Yazıyı kalın yapar.
        painter.setFont(font)  # Painter’a kullanılacak fontu verir.

        for number in range(1, FINAL_SQUARE + 1):  # 1’den son kareye kadar tüm kareleri dolaşır.
            row, col = self.get_row_col(number)  # Kare numarasının satır ve sütun değerini hesaplar.

            x = start_x + col * cell_size  # Karenin sol üst x koordinatını hesaplar.
            y = start_y + row * cell_size  # Karenin sol üst y koordinatını hesaplar.

            if (row + col) % 2 == 0:  # Satır ve sütun toplamına göre kare rengini dönüşümlü seçer.
                color = QColor(245, 238, 220)  # Açık bej renk belirler.
            else:
                color = QColor(220, 235, 245)  # Açık mavi renk belirler.

            painter.setBrush(QBrush(color))  # Karenin iç dolgu rengini ayarlar.
            painter.setPen(QPen(Qt.GlobalColor.black, 1))  # Karenin kenarlık rengini ve kalınlığını ayarlar.
            painter.drawRect(int(x), int(y), int(cell_size), int(cell_size))  # Kareyi ekrana çizer.

            painter.setPen(QPen(Qt.GlobalColor.black))  # Kare numarası için siyah yazı rengini ayarlar.
            painter.drawText(  # Kare numarasını karenin içine yazar.
                int(x + 5),  # Yazının x koordinatını belirler.
                int(y + 18),  # Yazının y koordinatını belirler.
                str(number)  # Kare numarasını metne çevirir.
            )

    def draw_ladders(self, painter, start_x, start_y, cell_size):  # Merdivenleri tahta üzerinde çizer.
        painter.setPen(QPen(QColor(130, 80, 30), 6))  # Merdivenin ana çizgisi için kahverengi ve kalın kalem ayarlar.

        for start, end in self.ladders.items():  # Tüm merdiven başlangıç ve bitiş karelerini dolaşır.
            start_point = self.get_cell_center(start, start_x, start_y, cell_size)  # Merdivenin başladığı karenin merkezini bulur.
            end_point = self.get_cell_center(end, start_x, start_y, cell_size)  # Merdivenin bittiği karenin merkezini bulur.

            painter.drawLine(start_point, end_point)  # Başlangıç ve bitiş arasında ana merdiven çizgisini çizer.

            painter.setPen(QPen(QColor(90, 50, 20), 2))  # Merdiven yan çizgileri için daha ince koyu kahverengi kalem ayarlar.

            dx = end_point.x() - start_point.x()  # Merdivenin yataydaki uzunluğunu hesaplar.
            dy = end_point.y() - start_point.y()  # Merdivenin dikeydeki uzunluğunu hesaplar.

            length = max((dx ** 2 + dy ** 2) ** 0.5, 1)  # Merdiven çizgisinin uzunluğunu hesaplar, sıfır bölmeyi engeller.
            offset_x = -dy / length * 10  # Merdivenin yan çizgileri için x yönünde kaydırma miktarını hesaplar.
            offset_y = dx / length * 10  # Merdivenin yan çizgileri için y yönünde kaydırma miktarını hesaplar.

            left_start = QPointF(start_point.x() + offset_x, start_point.y() + offset_y)  # Sol merdiven çizgisinin başlangıç noktasını hesaplar.
            left_end = QPointF(end_point.x() + offset_x, end_point.y() + offset_y)  # Sol merdiven çizgisinin bitiş noktasını hesaplar.
            right_start = QPointF(start_point.x() - offset_x, start_point.y() - offset_y)  # Sağ merdiven çizgisinin başlangıç noktasını hesaplar.
            right_end = QPointF(end_point.x() - offset_x, end_point.y() - offset_y)  # Sağ merdiven çizgisinin bitiş noktasını hesaplar.

            painter.drawLine(left_start, left_end)  # Merdivenin sol kenarını çizer.
            painter.drawLine(right_start, right_end)  # Merdivenin sağ kenarını çizer.

            for i in range(1, 5):  # Merdiven basamaklarını çizmek için 4 ara nokta oluşturur.
                t = i / 5  # Basamağın merdiven üzerindeki oransal konumunu hesaplar.
                p1 = QPointF(  # Basamağın sol kenardaki noktasını hesaplar.
                    left_start.x() + (left_end.x() - left_start.x()) * t,  # Sol basamak noktasının x koordinatını hesaplar.
                    left_start.y() + (left_end.y() - left_start.y()) * t,  # Sol basamak noktasının y koordinatını hesaplar.
                )
                p2 = QPointF(  # Basamağın sağ kenardaki noktasını hesaplar.
                    right_start.x() + (right_end.x() - right_start.x()) * t,  # Sağ basamak noktasının x koordinatını hesaplar.
                    right_start.y() + (right_end.y() - right_start.y()) * t,  # Sağ basamak noktasının y koordinatını hesaplar.
                )
                painter.drawLine(p1, p2)  # Merdiven basamağını çizer.

            painter.setPen(QPen(QColor(130, 80, 30), 6))  # Sonraki merdiven için ana kalemi tekrar ayarlar.

    def draw_snakes(self, painter, start_x, start_y, cell_size):  # Yılanları tahta üzerinde çizer.
        painter.setPen(QPen(QColor(40, 150, 70), 8))  # Yılan gövdesi için yeşil ve kalın kalem ayarlar.

        for start, end in self.snakes.items():  # Tüm yılan başlangıç ve bitiş karelerini dolaşır.
            start_point = self.get_cell_center(start, start_x, start_y, cell_size)  # Yılanın başladığı karenin merkezini bulur.
            end_point = self.get_cell_center(end, start_x, start_y, cell_size)  # Yılanın bittiği karenin merkezini bulur.

            middle_point = QPointF(  # Yılanın kıvrımlı görünmesi için orta kontrol noktası oluşturur.
                (start_point.x() + end_point.x()) / 2 + 25,  # Orta noktanın x koordinatını biraz sağa kaydırır.
                (start_point.y() + end_point.y()) / 2  # Orta noktanın y koordinatını hesaplar.
            )

            path_points = [start_point, middle_point, end_point]  # Yılanın çizileceği noktaları sıraya koyar.

            for i in range(len(path_points) - 1):  # Ardışık noktalar arasında çizgi çizmek için döner.
                painter.drawLine(path_points[i], path_points[i + 1])  # Yılan gövdesinin bir parçasını çizer.

            painter.setBrush(QBrush(QColor(30, 120, 50)))  # Yılan başı için dolgu rengini ayarlar.
            painter.setPen(QPen(QColor(20, 90, 40), 2))  # Yılan başı kenarlığı için kalem ayarlar.
            painter.drawEllipse(start_point, 9, 9)  # Yılanın başını daire/oval olarak çizer.

            painter.setBrush(QBrush(QColor(255, 255, 255)))  # Yılan gözleri için beyaz dolgu rengi ayarlar.
            painter.drawEllipse(QPointF(start_point.x() - 3, start_point.y() - 3), 2, 2)  # Sol gözü çizer.
            painter.drawEllipse(QPointF(start_point.x() + 3, start_point.y() - 3), 2, 2)  # Sağ gözü çizer.

            painter.setPen(QPen(QColor(40, 150, 70), 8))  # Sonraki yılan için gövde kalemini tekrar ayarlar.

    def draw_players(self, painter, start_x, start_y, cell_size):  # Oyuncu piyonlarını tahta üzerinde çizer.
        for player_id, position in self.player_positions.items():  # Tüm oyuncuların id ve pozisyonlarını dolaşır.
            if position <= 0:  # Oyuncu henüz tahtaya çıkmadıysa çizim yapmaz.
                continue  # Bu oyuncuyu atlayıp diğerine geçer.

            center = self.get_cell_center(position, start_x, start_y, cell_size)  # Oyuncunun bulunduğu karenin merkezini hesaplar.

            if player_id == 1:  # Oyuncu 1 için renk ve konum farkı belirler.
                color = QColor(220, 50, 50)  # Oyuncu 1 piyon rengini kırmızı yapar.
                offset = QPointF(-10, 10)  # Aynı karede çakışmayı azaltmak için piyonu biraz sola-aşağı kaydırır.
            else:
                color = QColor(50, 80, 220)  # Oyuncu 2 piyon rengini mavi yapar.
                offset = QPointF(10, -10)  # Aynı karede çakışmayı azaltmak için piyonu biraz sağa-yukarı kaydırır.

            player_center = QPointF(center.x() + offset.x(), center.y() + offset.y())  # Piyonun çizileceği nihai merkezi hesaplar.

            painter.setBrush(QBrush(color))  # Piyonun iç rengini ayarlar.
            painter.setPen(QPen(Qt.GlobalColor.black, 2))  # Piyon kenarlığı için siyah kalem ayarlar.
            painter.drawEllipse(player_center, 12, 12)  # Oyuncu piyonunu daire olarak çizer.

            painter.setPen(QPen(Qt.GlobalColor.white))  # Piyon üzerindeki oyuncu numarası için beyaz yazı rengi ayarlar.
            painter.drawText(  # Piyonun içine oyuncu numarasını yazar.
                int(player_center.x() - 4),  # Yazının x koordinatını ayarlar.
                int(player_center.y() + 5),  # Yazının y koordinatını ayarlar.
                str(player_id)  # Oyuncu id’sini yazıya çevirir.
            )

    def get_row_col(self, number):  # Kare numarasına göre tahtadaki satır ve sütun bilgisini hesaplar.
        index = number - 1  # Kare numarasını sıfır tabanlı indekse çevirir.

        row_from_bottom = index // BOARD_SIZE  # Karenin alttan kaçıncı satırda olduğunu hesaplar.
        col = index % BOARD_SIZE  # Karenin satır içindeki sütununu hesaplar.

        if row_from_bottom % 2 == 1:  # Yılanlar ve merdivenler tahtasında her ikinci satır ters yönde ilerler.
            col = BOARD_SIZE - 1 - col  # Ters satırlarda sütun yönünü çevirir.

        row = BOARD_SIZE - 1 - row_from_bottom  # PyQt koordinat sistemi yukarıdan başladığı için satırı ters çevirir.

        return row, col  # Hesaplanan satır ve sütun değerini döndürür.

    def get_cell_center(self, number, start_x, start_y, cell_size):  # Verilen kare numarasının merkez koordinatını hesaplar.
        row, col = self.get_row_col(number)  # Kare numarasının satır ve sütununu bulur.

        x = start_x + col * cell_size + cell_size / 2  # Karenin merkez x koordinatını hesaplar.
        y = start_y + row * cell_size + cell_size / 2  # Karenin merkez y koordinatını hesaplar.

        return QPointF(x, y)  # Merkez koordinatı QPointF olarak döndürür.