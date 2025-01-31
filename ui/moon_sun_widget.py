import datetime

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from utils import fetch_astral_data


class MoonSunWidget(QWidget):
    def __init__(self, city, region, timezone, lat, lon, parent=None):
        super().__init__(parent)
        self.city = city
        self.region = region
        self.timezone = timezone
        self.lat = lat
        self.lon = lon

        self.label = QLabel(self)
        self.label.setFont(QFont('Arial', 14))
        self.label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        # Update data immediately and then on a timer
        self.update_data()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(3600000)  # Update every hour

    def resizeEvent(self, event):
        # Make sure the label fills this widget
        self.label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def update_data(self):
        sunrise, sunset, phase_name = fetch_astral_data(self.city, self.region, self.timezone, self.lat, self.lon)

        sunrise_str = sunrise.strftime('%I:%M %p')
        sunset_str = sunset.strftime('%I:%M %p')

        display_text = (
            f"Moon: {phase_name}\n"
            f"Sunrise: {sunrise_str}\n"
            f"Sunset: {sunset_str}"
        )
        self.label.setText(display_text)
