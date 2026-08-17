from PySide6.QtCore import Qt, QRect, Signal
from PySide6.QtGui import (QColor, QCursor, QFont, QFontMetrics, QGuiApplication,
                           QPainter, QPen, QPixmap)
from PySide6.QtWidgets import QWidget, QApplication

from capture.screen import normalize_rect


def build_crosshair_cursor(size: int = 24, gap: int = 4) -> QCursor:
    """White crosshair with a black outline, hot point at the center."""
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    cx = cy = size // 2
    for pen in (QPen(QColor(0, 0, 0), 4), QPen(QColor(255, 255, 255), 2)):
        painter.setPen(pen)
        painter.drawLine(cx, 0, cx, cy - gap)
        painter.drawLine(cx, cy + gap, cx, size - 1)
        painter.drawLine(0, cy, cx - gap, cy)
        painter.drawLine(cx + gap, cy, size - 1, cy)
    painter.end()
    return QCursor(pm, cx, cy)


class CaptureOverlay(QWidget):
    region_selected = Signal(int, int, int, int)
    cancelled = Signal()

    MASK_COLOR = QColor(255, 255, 255, 140)
    RECT_COLOR = QColor(45, 127, 249)

    def __init__(self):
        super().__init__(None)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(build_crosshair_cursor())
        self._frozen = QPixmap()
        self._start = None
        self._end = None

    def start(self):
        screen = QApplication.primaryScreen()
        self._frozen = screen.grabWindow(0)
        self.setGeometry(screen.geometry())
        self.show()
        self.raise_()
        self.activateWindow()

    def crop_region(self, x: int, y: int, w: int, h: int) -> QPixmap:
        """Crop from the frozen frame so the captured pixels match what was shown."""
        if self._frozen.isNull():
            return QPixmap()
        dpr = self._frozen.devicePixelRatio()
        return self._frozen.copy(QRect(int(x * dpr), int(y * dpr), int(w * dpr), int(h * dpr)))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if not self._frozen.isNull():
            painter.drawPixmap(self.rect(), self._frozen, self._frozen.rect())
        painter.fillRect(self.rect(), self.MASK_COLOR)
        if self._start and self._end:
            left, top, w, h = normalize_rect(
                self._start.x(), self._start.y(), self._end.x(), self._end.y())
            rect = QRect(left, top, w, h)
            if not self._frozen.isNull():
                dpr = self._frozen.devicePixelRatio()
                source = QRect(int(left * dpr), int(top * dpr), int(w * dpr), int(h * dpr))
                painter.drawPixmap(rect, self._frozen, source)
            painter.setPen(QPen(self.RECT_COLOR, 2))
            painter.drawRect(rect)
            if w > 2 and h > 2:
                self._draw_size_label(painter, rect)

    def _draw_size_label(self, painter, rect):
        text = f"{rect.width()} × {rect.height()}"
        font = QFont("Segoe UI", 9)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        label_rect = QRect(rect.left(), rect.top() - text_height - 8,
                           text_width + 12, text_height + 6)
        if label_rect.top() < 0:
            label_rect.moveTop(rect.top() + 4)
        painter.fillRect(label_rect, QColor(0, 0, 0, 160))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(label_rect, Qt.AlignCenter, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start = event.position().toPoint()
            self._end = self._start
            self.update()

    def mouseMoveEvent(self, event):
        if self._start:
            self._end = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self._start:
            left, top, w, h = normalize_rect(
                self._start.x(), self._start.y(), self._end.x(), self._end.y())
            self.close()
            if w > 0 and h > 0:
                self.region_selected.emit(left, top, w, h)
            else:
                self.cancelled.emit()
            self._start = None
            self._end = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.cancelled.emit()
            self._start = None
            self._end = None
