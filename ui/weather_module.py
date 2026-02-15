import requests
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget

import config
from utils import fetch_weather


class WeatherWidget(QWidget):
    _ICON_SIZE   = 45   # px — scaled weather icon
    _ICON_WIDTH  = 60   # px — fixed width of the icon column
    _FONT_MAX    = 14
    _FONT_MIN    = 8

    def __init__(self, parent=None, api_key=None, city_name="Denver"):
        super().__init__(parent)
        self.api_key   = api_key
        self.city_name = city_name
        self._weather_text = "Loading weather…"

        # --- Icon column ---
        self.icon_label = QLabel(self)
        self.icon_label.setStyleSheet("background-color: rgba(0, 0, 0, 100);")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedWidth(self._ICON_WIDTH)

        # --- Text column ---
        self.text_label = QLabel(self._weather_text, self)
        self.text_label.setFont(QFont("Arial", self._FONT_MAX))
        self.text_label.setStyleSheet(
            "color: white; background-color: rgba(0, 0, 0, 100); padding: 5px;"
        )
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        layout.addWidget(self.icon_label, 0)
        layout.addWidget(self.text_label, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(config.WEATHER_REFRESH_MS)

        self.update_weather()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_font(self._weather_text)

    def _fit_font(self, text: str):
        """Scale the text label font down until the text fits, min _FONT_MIN pt."""
        available_w = self.width() - self._ICON_WIDTH - 30
        available_h = self.height() - 10
        if available_w <= 0 or available_h <= 0:
            return

        font = self.text_label.font()
        for size in range(self._FONT_MAX, self._FONT_MIN - 1, -1):
            font.setPointSize(size)
            rect = QFontMetrics(font).boundingRect(
                0, 0, available_w, available_h,
                Qt.AlignCenter | Qt.TextWordWrap,
                text,
            )
            if rect.width() <= available_w and rect.height() <= available_h:
                break
        self.text_label.setFont(font)

    # ------------------------------------------------------------------
    # Data refresh
    # ------------------------------------------------------------------

    def update_weather(self):
        try:
            data = fetch_weather(self.city_name, self.api_key)
        except Exception as exc:
            print(f"[weather] Fetch error: {exc}")
            self._show_error()
            return

        if data.get("cod") != 200:
            print(f"[weather] API error: {data.get('message', 'unknown')}")
            self._show_error()
            return

        temp        = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        icon_code   = data["weather"][0]["icon"]

        self._weather_text = f"{temp:.0f}°F\n{description}"
        self.text_label.setText(self._weather_text)
        self._fit_font(self._weather_text)
        self._load_icon(icon_code)

    def _load_icon(self, icon_code: str):
        url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        try:
            raw = requests.get(url, timeout=5).content
            src = QPixmap()
            src.loadFromData(raw)

            scaled = src.scaled(
                self._ICON_SIZE, self._ICON_SIZE,
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )

            # Centre the scaled icon within the fixed-width column
            canvas = QPixmap(self.icon_label.size())
            canvas.fill(Qt.transparent)
            x = (canvas.width()  - scaled.width())  // 2
            y = (canvas.height() - scaled.height()) // 2
            painter = QPainter(canvas)
            painter.drawPixmap(x, y, scaled)
            painter.end()

            self.icon_label.setPixmap(canvas)
        except Exception as exc:
            print(f"[weather] Icon error: {exc}")
            self.icon_label.clear()

    def _show_error(self):
        self._weather_text = "Weather\nunavailable"
        self.text_label.setText(self._weather_text)
        self.icon_label.clear()