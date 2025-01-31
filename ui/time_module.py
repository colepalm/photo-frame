from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, QDateTime, Qt


class TimeWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont('Arial', 18))
        self.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.setAlignment(Qt.AlignCenter)
        QTimer.singleShot(1000, self.update_time)  # Update time every second

    def update_time(self):
        now = QDateTime.currentDateTime()
        formatted_time = now.toString("hh:mm:ss")
        formatted_date = now.toString("dddd, MMMM dd")
        self.setText(f"{formatted_time}\n{formatted_date}")
        QTimer.singleShot(1000, self.update_time)  # Continuously update time
