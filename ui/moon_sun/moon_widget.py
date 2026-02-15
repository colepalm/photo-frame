from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QBrush, QPen


class MoonWidget(QWidget):
    """
    Renders the moon with the correct illuminated fraction and waxing/waning
    direction using QPainter path operations. No image assets required.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._fraction    = 0.0
        self._phase_angle = 0.0

    def set_phase(self, illumination_fraction: float, phase_angle: float):
        self._fraction    = max(0.0, min(1.0, illumination_fraction))
        self._phase_angle = phase_angle % 360
        self.update()

    def paintEvent(self, event):
        size = min(self.width(), self.height())
        r    = size / 2.0 - 2
        cx   = self.width()  / 2.0
        cy   = self.height() / 2.0

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        LIT  = QColor(255, 245, 200)
        DARK = QColor(30,  30,  50)

        disc = QPainterPath()
        disc.addEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
        painter.setClipPath(disc)
        painter.fillPath(disc, QBrush(DARK))

        frac   = self._fraction
        waxing = self._phase_angle < 180
        lit    = QPainterPath()

        if frac >= 0.99:
            lit.addEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
        elif frac > 0.01:
            term_x = r * abs(1.0 - 2.0 * frac)
            term   = QPainterPath()
            term.addEllipse(QRectF(cx - term_x, cy - r, term_x * 2, r * 2))

            if waxing:
                half = QPainterPath()
                half.moveTo(cx, cy - r)
                half.arcTo(QRectF(cx - r, cy - r, r * 2, r * 2), 90, -180)
                half.lineTo(cx, cy - r)
                lit = half.subtracted(term) if frac <= 0.5 else half.united(term)
            else:
                half = QPainterPath()
                half.moveTo(cx, cy - r)
                half.arcTo(QRectF(cx - r, cy - r, r * 2, r * 2), 90, 180)
                half.lineTo(cx, cy - r)
                lit = half.subtracted(term) if frac >= 0.5 else half.united(term)

        if not lit.isEmpty():
            painter.fillPath(lit, QBrush(LIT))

        painter.setClipping(False)
        painter.setPen(QPen(QColor(180, 170, 150, 80), 1.0))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
        painter.end()