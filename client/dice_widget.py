import random

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QBrush, QPen, QColor, QFont
from PyQt6.QtWidgets import QWidget


class DiceWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.value = 1
        self.final_value = 1
        self.animation_counter = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)

        self.setFixedSize(90, 90)

    def roll_animation(self):
        self.animation_counter = 12
        self.timer.start(80)

    def set_final_value(self, value):
        self.final_value = value

    def animate(self):
        if self.animation_counter > 0:
            self.value = random.randint(1, 6)
            self.animation_counter -= 1
            self.update()
        else:
            self.timer.stop()
            self.value = self.final_value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(QColor(255, 245, 210)))
        painter.setPen(QPen(QColor(180, 130, 40), 4))
        painter.drawRoundedRect(5, 5, 80, 80, 12, 12)

        painter.setBrush(QBrush(QColor(20, 20, 20)))
        painter.setPen(Qt.PenStyle.NoPen)

        dot_positions = self.get_dot_positions(self.value)

        for x, y in dot_positions:
            painter.drawEllipse(x, y, 10, 10)

        painter.setPen(QPen(QColor(80, 60, 20)))
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)

    def get_dot_positions(self, value):
        positions = {
            1: [(40, 40)],
            2: [(25, 25), (55, 55)],
            3: [(25, 25), (40, 40), (55, 55)],
            4: [(25, 25), (55, 25), (25, 55), (55, 55)],
            5: [(25, 25), (55, 25), (40, 40), (25, 55), (55, 55)],
            6: [(25, 22), (55, 22), (25, 40), (55, 40), (25, 58), (55, 58)],
        }

        return positions.get(value, positions[1])