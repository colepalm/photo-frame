from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt
from utils import fetch_weather


class WeatherWidget(QLabel):
    def __init__(self, parent=None, api_key=None, city_name='Denver'):
        super().__init__(parent)
        self.setFont(QFont('Arial', 16))
        self.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.setAlignment(Qt.AlignCenter)
        self.setText("Loading weather...")
        self.api_key = api_key
        self.city_name = city_name

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(600000)  # Update every 10 minutes
        self.update_weather()

    def update_weather(self):
        data = fetch_weather(self.city_name, self.api_key)
        if data and data.get("cod") == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            self.setText(f"{temp}°F, {description.capitalize()}")
        else:
            self.setText("Failed to retrieve weather data.")
