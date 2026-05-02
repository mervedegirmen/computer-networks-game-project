from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PyQt6.QtWidgets import QWidget

from common.constants import BOARD_SIZE, FINAL_SQUARE, SNAKES, LADDERS


class BoardWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.player_positions = {
            1: 0,
            2: 0,
        }

        self.snakes = SNAKES
        self.ladders = LADDERS

        self.setMinimumSize(620, 620)

    def update_board(self, player_positions):
        self.player_positions = {
            int(player): position
            for player, position in player_positions.items()
        }
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        board_size = min(self.width(), self.height()) - 40
        cell_size = board_size / BOARD_SIZE

        start_x = (self.width() - board_size) / 2
        start_y = (self.height() - board_size) / 2

        self.draw_cells(painter, start_x, start_y, cell_size)
        self.draw_ladders(painter, start_x, start_y, cell_size)
        self.draw_snakes(painter, start_x, start_y, cell_size)
        self.draw_players(painter, start_x, start_y, cell_size)

    def draw_cells(self, painter, start_x, start_y, cell_size):
        font = QFont()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)

        for number in range(1, FINAL_SQUARE + 1):
            row, col = self.get_row_col(number)

            x = start_x + col * cell_size
            y = start_y + row * cell_size

            if (row + col) % 2 == 0:
                color = QColor(245, 238, 220)
            else:
                color = QColor(220, 235, 245)

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(int(x), int(y), int(cell_size), int(cell_size))

            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.drawText(
                int(x + 5),
                int(y + 18),
                str(number)
            )

    def draw_ladders(self, painter, start_x, start_y, cell_size):
        painter.setPen(QPen(QColor(130, 80, 30), 6))

        for start, end in self.ladders.items():
            start_point = self.get_cell_center(start, start_x, start_y, cell_size)
            end_point = self.get_cell_center(end, start_x, start_y, cell_size)

            painter.drawLine(start_point, end_point)

            painter.setPen(QPen(QColor(90, 50, 20), 2))

            dx = end_point.x() - start_point.x()
            dy = end_point.y() - start_point.y()

            length = max((dx ** 2 + dy ** 2) ** 0.5, 1)
            offset_x = -dy / length * 10
            offset_y = dx / length * 10

            left_start = QPointF(start_point.x() + offset_x, start_point.y() + offset_y)
            left_end = QPointF(end_point.x() + offset_x, end_point.y() + offset_y)
            right_start = QPointF(start_point.x() - offset_x, start_point.y() - offset_y)
            right_end = QPointF(end_point.x() - offset_x, end_point.y() - offset_y)

            painter.drawLine(left_start, left_end)
            painter.drawLine(right_start, right_end)

            for i in range(1, 5):
                t = i / 5
                p1 = QPointF(
                    left_start.x() + (left_end.x() - left_start.x()) * t,
                    left_start.y() + (left_end.y() - left_start.y()) * t,
                )
                p2 = QPointF(
                    right_start.x() + (right_end.x() - right_start.x()) * t,
                    right_start.y() + (right_end.y() - right_start.y()) * t,
                )
                painter.drawLine(p1, p2)

            painter.setPen(QPen(QColor(130, 80, 30), 6))

    def draw_snakes(self, painter, start_x, start_y, cell_size):
        painter.setPen(QPen(QColor(40, 150, 70), 8))

        for start, end in self.snakes.items():
            start_point = self.get_cell_center(start, start_x, start_y, cell_size)
            end_point = self.get_cell_center(end, start_x, start_y, cell_size)

            middle_point = QPointF(
                (start_point.x() + end_point.x()) / 2 + 25,
                (start_point.y() + end_point.y()) / 2
            )

            path_points = [start_point, middle_point, end_point]

            for i in range(len(path_points) - 1):
                painter.drawLine(path_points[i], path_points[i + 1])

            painter.setBrush(QBrush(QColor(30, 120, 50)))
            painter.setPen(QPen(QColor(20, 90, 40), 2))
            painter.drawEllipse(start_point, 9, 9)

            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPointF(start_point.x() - 3, start_point.y() - 3), 2, 2)
            painter.drawEllipse(QPointF(start_point.x() + 3, start_point.y() - 3), 2, 2)

            painter.setPen(QPen(QColor(40, 150, 70), 8))

    def draw_players(self, painter, start_x, start_y, cell_size):
        for player_id, position in self.player_positions.items():
            if position <= 0:
                continue

            center = self.get_cell_center(position, start_x, start_y, cell_size)

            if player_id == 1:
                color = QColor(220, 50, 50)
                offset = QPointF(-10, 10)
            else:
                color = QColor(50, 80, 220)
                offset = QPointF(10, -10)

            player_center = QPointF(center.x() + offset.x(), center.y() + offset.y())

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawEllipse(player_center, 12, 12)

            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(
                int(player_center.x() - 4),
                int(player_center.y() + 5),
                str(player_id)
            )

    def get_row_col(self, number):
        index = number - 1

        row_from_bottom = index // BOARD_SIZE
        col = index % BOARD_SIZE

        if row_from_bottom % 2 == 1:
            col = BOARD_SIZE - 1 - col

        row = BOARD_SIZE - 1 - row_from_bottom

        return row, col

    def get_cell_center(self, number, start_x, start_y, cell_size):
        row, col = self.get_row_col(number)

        x = start_x + col * cell_size + cell_size / 2
        y = start_y + row * cell_size + cell_size / 2

        return QPointF(x, y)