import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
from datetime import datetime


class ForecastView(QWidget):
    """Full-screen forecast overlay view"""

    def __init__(self, parent, api_key, city_name):
        super().__init__(parent)
        self.api_key = api_key
        self.city_name = city_name

        # Set background with slight transparency
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 0, 0, 180);
                border-radius: 15px;
            }
        """)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(30)

        # Container for forecast days
        self.forecast_container = QHBoxLayout()
        self.forecast_container.setSpacing(20)
        self.main_layout.addLayout(self.forecast_container)

        # Store day widgets
        self.day_widgets = []

        # Create placeholder day widgets
        for i in range(7):
            day_widget = self.create_day_widget()
            self.day_widgets.append(day_widget)
            self.forecast_container.addWidget(day_widget)

        # Update forecast data
        self.update_forecast()

        # Set up timer to refresh every 30 minutes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_forecast)
        self.timer.start(1800000)  # 30 minutes

    def create_day_widget(self):
        """Create a widget for a single day's forecast"""
        day_frame = QFrame()
        day_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(50, 50, 50, 120);
                border-radius: 10px;
            }
        """)
        day_frame.setMinimumWidth(180)
        day_frame.setMaximumWidth(220)
        day_frame.setMinimumHeight(320)
        day_frame.setMaximumHeight(340)

        layout = QVBoxLayout(day_frame)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)

        # Day name
        day_label = QLabel("Day")
        day_label.setStyleSheet("""
            color: white;
            font-size: 22px;
            font-weight: bold;
            background-color: transparent;
        """)
        day_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(day_label)

        # Weather icon (placeholder)
        icon_label = QLabel("☀️")
        icon_label.setStyleSheet("""
            color: white;
            font-size: 56px;
            background-color: transparent;
        """)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # High temperature
        high_temp_label = QLabel("--°")
        high_temp_label.setStyleSheet("""
            color: #FF6B6B;
            font-size: 28px;
            font-weight: bold;
            background-color: transparent;
        """)
        high_temp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(high_temp_label)

        # Low temperature
        low_temp_label = QLabel("--°")
        low_temp_label.setStyleSheet("""
            color: #4ECDC4;
            font-size: 24px;
            background-color: transparent;
        """)
        low_temp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(low_temp_label)

        # Weather description
        desc_label = QLabel("Loading...")
        desc_label.setStyleSheet("""
            color: #CCCCCC;
            font-size: 14px;
            background-color: transparent;
        """)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Store references to labels
        day_frame.day_label = day_label
        day_frame.icon_label = icon_label
        day_frame.high_temp_label = high_temp_label
        day_frame.low_temp_label = low_temp_label
        day_frame.desc_label = desc_label

        return day_frame

    def get_weather_emoji(self, weather_id):
        """Convert weather ID to emoji/symbol"""
        if 200 <= weather_id < 300:
            return "⚡"
        elif 300 <= weather_id < 400:
            return "🌦"
        elif 500 <= weather_id < 600:
            return "☔"
        elif 600 <= weather_id < 700:
            return "❄"
        elif 700 <= weather_id < 800:
            return "≡"
        elif weather_id == 800:
            return "☀"
        elif weather_id == 801:
            return "🌤"
        elif weather_id == 802:
            return "⛅"
        elif weather_id > 802:
            return "☁"
        return "🌡"

    def update_forecast(self):
        """Fetch and update forecast data"""
        try:
            # OpenWeatherMap API call for 7-day forecast
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={self.city_name}&appid={self.api_key}&units=imperial"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                forecasts = {}

                # Group by day
                for entry in data['list']:
                    date = datetime.fromtimestamp(entry['dt']).date()
                    if date not in forecasts:
                        forecasts[date] = {
                            "temps": [],
                            "weather": []
                        }
                    forecasts[date]["temps"].append(entry['main']['temp'])
                    forecasts[date]["weather"].append(entry['weather'][0])

                # Process available days (5-day forecast gives us ~5-6 days)
                day_count = 0
                for i, (date, values) in enumerate(list(forecasts.items())):
                    if day_count >= len(self.day_widgets):
                        break

                    day_widget = self.day_widgets[day_count]

                    # Day name
                    today = datetime.now().date()
                    if date == today:
                        day_name = "Today"
                    elif date == today.replace(day=today.day + 1):
                        day_name = "Tomorrow"
                    else:
                        day_name = date.strftime("%A")
                    day_widget.day_label.setText(day_name)

                    # Temps
                    high_temp = round(max(values['temps']))
                    low_temp = round(min(values['temps']))
                    day_widget.high_temp_label.setText(f"{high_temp}°")
                    day_widget.low_temp_label.setText(f"{low_temp}°")

                    # Choose a representative weather (e.g. midday entry)
                    rep_weather = values['weather'][len(values['weather']) // 2]
                    weather_id = rep_weather['id']
                    emoji = self.get_weather_emoji(weather_id)
                    day_widget.icon_label.setText(emoji)

                    description = rep_weather['description'].title()
                    day_widget.desc_label.setText(description)

                    day_widget.show()
                    day_count += 1

                # Hide unused day widgets
                for i in range(day_count, len(self.day_widgets)):
                    self.day_widgets[i].hide()

                print(f"Forecast updated successfully - {day_count} days displayed")
            else:
                print(f"Error fetching forecast: {response.status_code}")

        except Exception as e:
            print(f"Error updating forecast: {e}")