from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


class TimeWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Arial", 14))
        self.setStyleSheet(
            "color: white;"
            "background-color: rgba(0, 0, 0, 100);"
            "border-radius: 10px;"
            "padding: 5px;"
        )
        self.setAlignment(Qt.AlignCenter)

        self._tick()

    def _tick(self):
        now = QDateTime.currentDateTime()
        self.setText(
            f"{now.toString('h:mm AP')}\n"
            f"{now.toString('ddd, MMMM d')}"
        )

        # Schedule the next tick at the top of the next second
        ms_remaining = 1000 - now.time().msec()
        QTimer.singleShot(ms_remaining, self._tick)