import datetime

import requests
from PyQt5.QtCore import QByteArray, QTimer, Qt
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

import config


# ---------------------------------------------------------------------------
# SVG icon data keyed by weather condition bucket
# ---------------------------------------------------------------------------

_SVG_ICONS: dict[str, str] = {
    "clear": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <circle cx="32" cy="32" r="12" fill="#FFD700"/>
        <line x1="32" y1="8"  x2="32" y2="16" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="32" y1="48" x2="32" y2="56" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="8"  y1="32" x2="16" y2="32" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="48" y1="32" x2="56" y2="32" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="14" y1="14" x2="20" y2="20" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="44" y1="44" x2="50" y2="50" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="50" y1="14" x2="44" y2="20" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
        <line x1="20" y1="44" x2="14" y2="50" stroke="#FFD700" stroke-width="3" stroke-linecap="round"/>
    </svg>""",

    "partly_cloudy": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <circle cx="24" cy="20" r="10" fill="#FFD700"/>
        <line x1="24" y1="6"  x2="24" y2="12" stroke="#FFD700" stroke-width="2" stroke-linecap="round"/>
        <line x1="10" y1="20" x2="16" y2="20" stroke="#FFD700" stroke-width="2" stroke-linecap="round"/>
        <ellipse cx="35" cy="40" rx="16" ry="11" fill="#BDC3C7"/>
        <ellipse cx="22" cy="38" rx="12" ry="9"  fill="#95A5A6"/>
    </svg>""",

    "cloudy": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="28" cy="36" rx="16" ry="12" fill="#95A5A6"/>
        <ellipse cx="40" cy="32" rx="14" ry="10" fill="#BDC3C7"/>
        <ellipse cx="20" cy="32" rx="12" ry="9"  fill="#7F8C8D"/>
    </svg>""",

    "rain": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="32" cy="24" rx="18" ry="12" fill="#95A5A6"/>
        <line x1="22" y1="38" x2="20" y2="48" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="32" y1="38" x2="30" y2="48" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="42" y1="38" x2="40" y2="48" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
    </svg>""",

    "snow": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="32" cy="24" rx="18" ry="12" fill="#95A5A6"/>
        <circle cx="22" cy="42" r="3" fill="#ECF0F1"/>
        <circle cx="32" cy="44" r="3" fill="#ECF0F1"/>
        <circle cx="42" cy="42" r="3" fill="#ECF0F1"/>
        <circle cx="27" cy="50" r="3" fill="#ECF0F1"/>
        <circle cx="37" cy="50" r="3" fill="#ECF0F1"/>
    </svg>""",

    "thunderstorm": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="32" cy="20" rx="18" ry="12" fill="#7F8C8D"/>
        <polygon points="32,28 28,40 34,40 30,52 38,36 32,36" fill="#FFD700"/>
    </svg>""",

    "drizzle": """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="32" cy="24" rx="18" ry="12" fill="#BDC3C7"/>
        <line x1="20" y1="38" x2="20" y2="44" stroke="#5DADE2" stroke-width="2" stroke-linecap="round"/>
        <line x1="28" y1="40" x2="28" y2="46" stroke="#5DADE2" stroke-width="2" stroke-linecap="round"/>
        <line x1="36" y1="38" x2="36" y2="44" stroke="#5DADE2" stroke-width="2" stroke-linecap="round"/>
        <line x1="44" y1="40" x2="44" y2="46" stroke="#5DADE2" stroke-width="2" stroke-linecap="round"/>
    </svg>""",
}


def _weather_icon_key(weather_id: int) -> str:
    """Map an OWM weather condition ID to an _SVG_ICONS key."""
    if weather_id == 800:
        return "clear"
    if weather_id in (801, 802):
        return "partly_cloudy"
    if weather_id > 802:
        return "cloudy"
    if 500 <= weather_id < 600:
        return "rain"
    if 600 <= weather_id < 700:
        return "snow"
    if 200 <= weather_id < 300:
        return "thunderstorm"
    return "drizzle"


def _svg_to_pixmap(svg: str, size: int = 80) -> QPixmap:
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def _day_label(date: datetime.date) -> str:
    today = datetime.date.today()
    if date == today:
        return "Today"
    if date == today + datetime.timedelta(days=1):
        return "Tomorrow"
    return date.strftime("%A")


# ---------------------------------------------------------------------------
# Per-day card widget
# ---------------------------------------------------------------------------

class _DayCard(QFrame):
    """A single day column in the forecast strip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "QFrame { background-color: rgba(50, 50, 50, 120); border-radius: 10px; }"
        )
        self.setFixedWidth(200)
        self.setMinimumHeight(320)
        self.setMaximumHeight(340)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 30, 20, 20)

        def _label(text, style):
            lbl = QLabel(text, self)
            lbl.setStyleSheet(style + " background-color: transparent;")
            lbl.setAlignment(Qt.AlignCenter)
            return lbl

        self.day_label  = _label("—",        "color: white; font-size: 22px; font-weight: bold;")
        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background-color: transparent;")
        self.high_label = _label("--°",       "color: #FF6B6B; font-size: 28px; font-weight: bold;")
        self.low_label  = _label("--°",       "color: #4ECDC4; font-size: 24px;")
        self.desc_label = _label("Loading…",  "color: #CCCCCC; font-size: 14px;")
        self.desc_label.setWordWrap(True)

        for widget in (self.day_label, self.icon_label,
                       self.high_label, self.low_label, self.desc_label):
            layout.addWidget(widget, 0, Qt.AlignCenter)

    def populate(self, date: datetime.date, high: int, low: int,
                 weather_id: int, description: str):
        self.day_label.setText(_day_label(date))
        self.high_label.setText(f"{high}°")
        self.low_label.setText(f"{low}°")
        self.desc_label.setText(description.title())
        svg = _SVG_ICONS[_weather_icon_key(weather_id)]
        self.icon_label.setPixmap(_svg_to_pixmap(svg))


# ---------------------------------------------------------------------------
# ForecastView
# ---------------------------------------------------------------------------

class ForecastView(QWidget):
    """Full-screen forecast overlay — shows up to 7 days."""

    _API_URL = (
        "https://api.openweathermap.org/data/2.5/forecast"
        "?q={city}&appid={key}&units=imperial"
    )

    def __init__(self, parent, api_key: str, city_name: str):
        super().__init__(parent)
        self.api_key   = api_key
        self.city_name = city_name

        self.setStyleSheet(
            "QWidget { background-color: rgba(0, 0, 0, 180); border-radius: 15px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        self._card_row = QHBoxLayout()
        self._card_row.setSpacing(20)
        layout.addLayout(self._card_row)

        self._cards: list[_DayCard] = [_DayCard(self) for _ in range(7)]
        for card in self._cards:
            self._card_row.addWidget(card)

        self.update_forecast()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_forecast)
        self.timer.start(config.WEATHER_REFRESH_MS)

    # ------------------------------------------------------------------
    # Data fetching
    # ------------------------------------------------------------------

    def update_forecast(self):
        url = self._API_URL.format(city=self.city_name, key=self.api_key)
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            self._apply(response.json())
        except requests.HTTPError as exc:
            print(f"[forecast] HTTP error: {exc}")
        except requests.RequestException as exc:
            print(f"[forecast] Network error: {exc}")
        except Exception as exc:
            print(f"[forecast] Unexpected error: {exc}")

    def _apply(self, data: dict):
        # Group 3-hourly entries by calendar date
        by_day: dict[datetime.date, dict] = {}
        for entry in data["list"]:
            date = datetime.datetime.fromtimestamp(entry["dt"]).date()
            bucket = by_day.setdefault(date, {"temps": [], "weather": []})
            bucket["temps"].append(entry["main"]["temp"])
            bucket["weather"].append(entry["weather"][0])

        visible = 0
        for card, (date, values) in zip(self._cards, by_day.items()):
            midday = values["weather"][len(values["weather"]) // 2]
            card.populate(
                date        = date,
                high        = round(max(values["temps"])),
                low         = round(min(values["temps"])),
                weather_id  = midday["id"],
                description = midday["description"],
            )
            card.show()
            visible += 1

        for card in self._cards[visible:]:
            card.hide()

        print(f"[forecast] Updated — {visible} days displayed.")