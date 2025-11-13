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
        self.event_label.setFont(QFont('Arial', 14))
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

    def is_all_day_event(self, event):
        """Check if an event is an all-day event."""
        return 'date' in event['start'] and 'dateTime' not in event['start']

    def format_event(self, event, is_all_day=False):
        """Format a single event for display."""
        summary = event.get('summary', 'No Title')

        if is_all_day:
            # For all-day events, just show the date and title
            start = event['start'].get('date')
            start_dt = datetime.datetime.fromisoformat(start)
            formatted_start = start_dt.strftime('%b %d')
            event_text = f"{formatted_start}: {summary}"
        else:
            start = event['start'].get('dateTime', event['start'].get('date'))
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            formatted_date = start_dt.strftime('%b %d')
            formatted_time = start_dt.strftime('%I:%M %p')
            event_text = f"{formatted_date} {formatted_time}\n{summary}"

        return event_text

    def update_event(self):
        # Fetch more events to find both all-day and timed events
        events = fetch_calendar_events(self.service, max_results=5)

        if not events:
            self.event_label.setText("No upcoming events found.")
            return

        all_day_events = []
        timed_events = []

        # Separate all-day and timed events
        for event in events:
            if self.is_all_day_event(event):
                all_day_events.append(event)
            else:
                timed_events.append(event)

        display_parts = []

        if all_day_events:
            display_parts.append(self.format_event(all_day_events[0], is_all_day=True))

        if timed_events:
            if display_parts:
                display_parts.append("")  # Add spacing
            display_parts.append(self.format_event(timed_events[0], is_all_day=False))

        # If we only have all-day events, show just the first one
        if all_day_events and not timed_events:
            display_parts = [self.format_event(all_day_events[0], is_all_day=True)]

        self.event_label.setText("\n".join(display_parts))