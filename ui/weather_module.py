from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QFontMetrics, QPainter
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
        self.icon_label.setFixedWidth(60)
        self.icon_label.setScaledContents(False)

        self.current_weather_text = "Loading weather..."
        self.text_label = QLabel("Loading weather...")
        self.text_label.setFont(QFont('Arial', 14))
        self.text_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100); padding: 5px;")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setScaledContents(True)

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.addWidget(self.icon_label, 0)
        layout.addWidget(self.text_label, 1)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(600_000)

        self.update_weather()

    def adjust_font_size(self, text, max_width, max_height):
        """Dynamically adjust font size to fit the available space."""
        font = self.text_label.font()
        font_size = 14

        while font_size > 8:  # Minimum font size
            font.setPointSize(font_size)
            metrics = QFontMetrics(font)

            # Check if text fits within the available space
            text_rect = metrics.boundingRect(0, 0, max_width, max_height,
                                             Qt.AlignCenter | Qt.TextWordWrap, text)

            if text_rect.width() <= max_width and text_rect.height() <= max_height:
                break

            font_size -= 1

        self.text_label.setFont(font)

    def resizeEvent(self, event):
        """Handle resize events to adjust font size."""
        super().resizeEvent(event)
        if hasattr(self, 'current_weather_text'):
            # Get available width for text (total width minus icon and margins)
            available_width = self.width() - self.icon_label.width() - 30  # 30 for margins/spacing
            available_height = self.height() - 10  # 10 for margins

            if available_width > 0 and available_height > 0:
                self.adjust_font_size(self.current_weather_text, available_width, available_height)

    def update_weather(self):
        """Fetch weather data and update icon + text."""
        data = fetch_weather(self.city_name, self.api_key)
        if data and data.get("cod") == 200:
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"].capitalize()

            # Store current text for resize handling
            self.current_weather_text = f"{temp:.0f}°F\n{description}"

            # Extract icon code (e.g., "04d")
            icon_code = data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            try:
                icon_data = requests.get(icon_url).content
                pixmap = QPixmap()
                pixmap.loadFromData(icon_data)

                # Create a new pixmap with the label size and fill with transparent
                label_size = self.icon_label.size()
                centered_pixmap = QPixmap(label_size)
                centered_pixmap.fill(Qt.transparent)

                # Scale the original icon to a reasonable size (smaller than label)
                scaled_icon = pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Calculate position to center the scaled icon
                x = (label_size.width() - scaled_icon.width()) // 2
                y = (label_size.height() - scaled_icon.height()) // 2

                # Draw the scaled icon onto the centered pixmap
                from PyQt5.QtGui import QPainter
                painter = QPainter(centered_pixmap)
                painter.drawPixmap(x, y, scaled_icon)
                painter.end()

                self.icon_label.setPixmap(centered_pixmap)
            except Exception as e:
                print(f"Error fetching icon: {e}")
                self.icon_label.clear()

            # Update text with line break for better formatting
            self.text_label.setText(self.current_weather_text)

            # Adjust font size based on current widget size
            if self.width() > 0 and self.height() > 0:
                available_width = self.width() - self.icon_label.width() - 30
                available_height = self.height() - 10
                if available_width > 0 and available_height > 0:
                    self.adjust_font_size(self.current_weather_text, available_width, available_height)
        else:
            self.current_weather_text = "Weather data\nunavailable"
            self.text_label.setText(self.current_weather_text)
            self.icon_label.clear()

    def set_max_size(self, width, height):
        """Set maximum size constraints for the widget."""
        self.setMaximumSize(width, height)

    def set_min_size(self, width, height):
        """Set minimum size constraints for the widget."""
        self.setMinimumSize(width, height)