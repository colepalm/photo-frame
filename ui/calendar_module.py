import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from utils import fetch_calendar_events
from calendar_service import get_calendar_service


class CalendarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = get_calendar_service()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.event_label = QLabel(self)
        self.event_label.setFont(QFont('Arial', 18))
        self.event_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")
        self.event_label.setAlignment(Qt.AlignCenter)
        self.event_label.setWordWrap(True)

        self.update_event()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_event)
        self.timer.start(600000)  # Update every 10 minutes

    def resizeEvent(self, event):
        """Ensure the label fills the widget."""
        self.event_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def update_event(self):
        events = fetch_calendar_events(self.service)
        if not events:
            self.event_label.setText("No upcoming events found.")
        else:
            event = events[0]
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            formatted_start = start_dt.strftime('%a, %b %d %I:%M %p')
            summary = event.get('summary', 'No Title')
            location = event.get('location', '')
            event_text = f"{formatted_start}\n{summary}"
            if location:
                event_text += f"\nLocation: {location}"
            self.event_label.setText(event_text)