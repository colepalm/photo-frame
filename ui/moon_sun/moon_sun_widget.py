import traceback

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

import config
from utils import fetch_astral_data
from ui.moon_sun.moon_widget import MoonWidget


class MoonSunWidget(QWidget):
    _MOON_SIZE = 70

    def __init__(self, city, region, timezone, lat, lon, parent=None):
        super().__init__(parent)
        self.city     = city
        self.region   = region
        self.timezone = timezone
        self.lat      = lat
        self.lon      = lon

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "MoonSunWidget {"
            "  background-color: rgba(0, 0, 0, 100);"
            "  border-radius: 10px;"
            "}"
            "QLabel { background-color: transparent; }"
        )

        self._build_ui()

        self.update_data()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(config.ASTRAL_REFRESH_MS)

    def _label(self, size: int, bold=False, dim=False) -> QLabel:
        lbl = QLabel(self)
        f   = QFont("Arial", size)
        f.setBold(bold)
        lbl.setFont(f)
        lbl.setStyleSheet(
            "color: rgba(255,255,255,150);" if dim else "color: white;"
        )
        lbl.setAlignment(Qt.AlignCenter)
        return lbl

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        # Moon disc
        self.moon_widget = MoonWidget(self)
        self.moon_widget.setFixedSize(self._MOON_SIZE, self._MOON_SIZE)
        moon_row = QHBoxLayout()
        moon_row.addStretch()
        moon_row.addWidget(self.moon_widget)
        moon_row.addStretch()
        root.addLayout(moon_row)

        root.addSpacing(8)

        # Sunrise · Sunset · Daylight columns
        sun_row = QHBoxLayout()
        sun_row.setSpacing(0)
        for attr, header in (
            ("sunrise_label",  "Sunrise"),
            ("sunset_label",   "Sunset"),
            ("daylight_label", "Daylight"),
        ):
            col = QVBoxLayout()
            col.setContentsMargins(0, 0, 0, 0)
            hdr = self._label(8, dim=True)
            hdr.setText(header)
            val = self._label(11, bold=True)
            setattr(self, attr, val)
            col.addWidget(hdr)
            col.addWidget(val)
            sun_row.addStretch()
            sun_row.addLayout(col)
        sun_row.addStretch()
        root.addLayout(sun_row)

    def update_data(self):
        try:
            data = fetch_astral_data(
                self.city, self.region, self.timezone, self.lat, self.lon
            )
        except Exception:
            traceback.print_exc()
            self._show_error()
            return

        self.moon_widget.set_phase(data.illumination, data.phase_angle)
        self.sunrise_label.setText(data.sunrise.strftime("%-I:%M %p"))
        self.sunset_label.setText(data.sunset.strftime("%-I:%M %p"))

        total_s  = int((data.sunset - data.sunrise).total_seconds())
        hours, r = divmod(total_s, 3600)
        self.daylight_label.setText(f"{hours}h {r // 60:02d}m")

    def _show_error(self):
        self.sunrise_label.setText("—")
        self.sunset_label.setText("—")
        self.daylight_label.setText("—")