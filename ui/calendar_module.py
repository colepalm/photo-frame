import datetime

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

import config
from calendar_service import get_calendar_service
from utils import fetch_calendar_events


class CalendarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = get_calendar_service()

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            "CalendarWidget {"
            "  background-color: rgba(0, 0, 0, 100);"
            "  border-radius: 10px;"
            "}"
            "QLabel { background-color: transparent; color: white; padding: 5px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.event_label = QLabel(self)
        self.event_label.setFont(QFont("Arial", 14))
        self.event_label.setAlignment(Qt.AlignCenter)
        self.event_label.setWordWrap(True)
        layout.addWidget(self.event_label)

        self.setFixedWidth(250)
        self.setFixedHeight(160)

        self.update_event()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_event)
        self.timer.start(config.CALENDAR_REFRESH_MS)

    @staticmethod
    def _is_all_day(event: dict) -> bool:
        return "date" in event["start"] and "dateTime" not in event["start"]

    @staticmethod
    def _format_all_day(event: dict) -> str:
        dt = datetime.date.fromisoformat(event["start"]["date"])
        return f"{dt.strftime('%m/%d')}: {event.get('summary', 'No Title')}"

    @staticmethod
    def _format_timed(event: dict) -> str:
        raw = event["start"].get("dateTime", event["start"].get("date", ""))
        dt  = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return (
            f"{dt.strftime('%m/%d')} {dt.strftime('%-I:%M %p')}\n"
            f"{event.get('summary', 'No Title')}"
        )

    def update_event(self):
        events = fetch_calendar_events(self.service, max_results=5)
        if not events:
            self.event_label.setText("No upcoming events.")
            return

        all_day = [e for e in events if self._is_all_day(e)]
        timed   = [e for e in events if not self._is_all_day(e)]

        parts = []
        if all_day:
            parts.append(self._format_all_day(all_day[0]))
        if timed:
            parts.append(self._format_timed(timed[0]))

        self.event_label.setText("\n\n".join(parts) if parts else "No upcoming events.")