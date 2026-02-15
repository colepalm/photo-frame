import io
import random

from PIL import Image, ImageOps
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget

import config
from ui.calendar_module import CalendarWidget
from ui.forecast_view import ForecastView
from ui.moon_sun.moon_sun_widget import MoonSunWidget
from ui.time_module import TimeWidget
from ui.weather_module import WeatherWidget
from utils import load_photos


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def load_and_process_image(image_path: str) -> QPixmap:
    """Load an image file, correct EXIF orientation, and return a QPixmap."""
    try:
        with Image.open(image_path) as img:
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            img = ImageOps.exif_transpose(img)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            return pixmap

    except Exception as exc:
        print(f"[main_window] Error processing image {image_path}: {exc}")
        return QPixmap(image_path)   # fallback: let Qt load it directly


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")
        self._setup_done = False
        self.current_pixmap: QPixmap | None = None
        self.showing_forecast = False

        # --- Root widget ---
        central = QWidget(self)
        self.setCentralWidget(central)
        central.setStyleSheet("background-color: black;")

        # --- Background image ---
        self.image_label = QLabel(central)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)

        # --- Overlay widgets ---
        self.weather_widget = WeatherWidget(
            central, config.WEATHER_API_KEY, config.WEATHER_CITY
        )

        self.time_widget = TimeWidget(central)

        self.calendar_widget = CalendarWidget(central)

        self.moon_sun_widget = MoonSunWidget(
            city=config.CITY,
            region=config.REGION,
            timezone=config.TIMEZONE,
            lat=config.LATITUDE,
            lon=config.LONGITUDE,
            parent=central,
        )

        self.forecast_view = ForecastView(
            central, config.WEATHER_API_KEY, config.WEATHER_CITY
        )
        self.forecast_view.hide()

        # --- Timers ---
        self.photo_timer = QTimer(self)
        self.photo_timer.timeout.connect(self.advance_photo)
        self.photo_timer.start(config.PHOTO_INTERVAL_MS)

        self.forecast_show_timer = QTimer(self)
        self.forecast_show_timer.timeout.connect(self.show_forecast_temporarily)
        self.forecast_show_timer.start(config.FORECAST_SHOW_INTERVAL_MS)

        self.forecast_hide_timer = QTimer(self)
        self.forecast_hide_timer.timeout.connect(self.hide_forecast)
        self.forecast_hide_timer.setSingleShot(True)

        # --- Photo list ---
        self.photos_list = load_photos()
        random.shuffle(self.photos_list)
        self.current_photo = 0

        # --- First paint ---
        self.advance_photo()
        self.update_positions()
        self._setup_done = True
        self.showFullScreen()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def resizeEvent(self, event):
        if self._setup_done:
            self.update_positions()
            self._rescale_current_image()
        super().resizeEvent(event)

    def update_positions(self):
        """Place every overlay widget relative to the current window size."""
        w = self.width()
        h = self.height()
        margin = 20

        self.image_label.setGeometry(0, 0, w, h)

        # Top-right: weather
        ww_w = min(280, w // 4)
        ww_h = min(100, h // 15)
        self.weather_widget.setGeometry(w - ww_w - margin, margin, ww_w, ww_h)

        # Bottom-right: time
        tw_w, tw_h = 200, 60
        self.time_widget.setGeometry(w - tw_w - margin, h - tw_h - margin, tw_w, tw_h)

        # Bottom-left: calendar (self-sizing height)
        cw_w = 250
        self.calendar_widget.setFixedWidth(cw_w)
        self.calendar_widget.adjustSize()
        self.calendar_widget.move(margin, h - self.calendar_widget.height() - 40)

        # Top-left: moon + sun
        self.moon_sun_widget.setGeometry(
            margin, margin, config.MOON_SUN_WIDTH, config.MOON_SUN_HEIGHT
        )

        if self.showing_forecast:
            self._position_forecast()

    # ------------------------------------------------------------------
    # Photos
    # ------------------------------------------------------------------

    def advance_photo(self):
        """Load the next photo, cycling and reshuffling when the list wraps."""
        if not self.photos_list:
            print("[main_window] No images found.")
            return

        path = self.photos_list[self.current_photo]
        print(f"[main_window] Loading: {path}")

        self.current_pixmap = load_and_process_image(path)
        self._rescale_current_image()

        self.current_photo += 1
        if self.current_photo >= len(self.photos_list):
            self.current_photo = 0
            random.shuffle(self.photos_list)   # reshuffle on each full cycle

    def _rescale_current_image(self):
        if self.current_pixmap:
            scaled = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled)

    # ------------------------------------------------------------------
    # Forecast overlay
    # ------------------------------------------------------------------

    def show_forecast_temporarily(self):
        if not self.showing_forecast:
            self._position_forecast()
            self.forecast_view.show()
            self.forecast_view.raise_()
            self.showing_forecast = True
            self.forecast_hide_timer.start(config.FORECAST_DISPLAY_DURATION_MS)

    def hide_forecast(self):
        self.forecast_view.hide()
        self.showing_forecast = False

    def _position_forecast(self):
        margin = 50
        self.forecast_view.setGeometry(
            margin, margin,
            self.width()  - margin * 2,
            self.height() - margin * 2,
        )