from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer
import requests

from utils import fetch_weather


class WeatherWidget(QWidget):
    def __init__(self, parent=None, api_key=None, city_name='Denver'):
        super().__init__(parent)
        self.api_key = api_key
        self.city_name = city_name

        self.icon_label = QLabel()
        self.icon_label.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel("Loading weather...")
        self.text_label.setFont(QFont('Arial', 18))
        self.text_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.text_label.setAlignment(Qt.AlignCenter)

        layout = QHBoxLayout()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(600_000)

        self.update_weather()

    def update_weather(self):
        """Fetch weather data and update icon + text."""
        data = fetch_weather(self.city_name, self.api_key)
        if data and data.get("cod") == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"].capitalize()

            # Extract icon code (e.g., "04d")
            icon_code = data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            try:
                icon_data = requests.get(icon_url).content
                pixmap = QPixmap()
                pixmap.loadFromData(icon_data)

                pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                self.icon_label.setPixmap(pixmap)
            except Exception as e:
                print(f"Error fetching icon: {e}")
                self.icon_label.clear()

            # Update text
            self.text_label.setText(f"{temp:.0f}°F, {description}")
        else:
            self.text_label.setText("Failed to retrieve weather data.")
            self.icon_label.clear()
