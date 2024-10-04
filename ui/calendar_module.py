from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

from utils import fetch_calendar_events
from google_calendar_service import get_calendar_service


class CalendarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = get_calendar_service()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("Upcoming Events")
        self.title.setFont(QFont('Arial', 18, QFont.Bold))
        self.title.setStyleSheet("color: white;")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.events_labels = []

        self.update_events()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_events)
        self.timer.start(600000)  # Update every 10 minutes

    def update_events(self):
        # Clear old event labels
        for label in self.events_labels:
            self.layout.removeWidget(label)
            label.deleteLater()
        self.events_labels.clear()

        events = fetch_calendar_events(self.service)
        if not events:
            no_events_label = QLabel("No upcoming events found.")
            no_events_label.setFont(QFont('Arial', 14))
            no_events_label.setStyleSheet("color: white;")
            no_events_label.setAlignment(Qt.AlignCenter)
            self.layout.addWidget(no_events_label)
            self.events_labels.append(no_events_label)
        else:
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                event_label = QLabel(f"{start} - {event['summary']}")
                event_label.setFont(QFont('Arial', 14))
                event_label.setStyleSheet("color: white;")
                event_label.setAlignment(Qt.AlignLeft)
                self.layout.addWidget(event_label)
                self.events_labels.append(event_label)
