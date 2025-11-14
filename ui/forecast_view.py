import requests

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer, QByteArray
from PyQt5.QtSvg import QSvgWidget
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

        # Weather icon - using SVG widget
        icon_widget = QSvgWidget()
        icon_widget.setFixedSize(64, 64)
        layout.addWidget(icon_widget)

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
        day_frame.icon_widget = icon_widget
        day_frame.high_temp_label = high_temp_label
        day_frame.low_temp_label = low_temp_label
        day_frame.desc_label = desc_label

        return day_frame

    def get_weather_svg(self, weather_id):
        """Return SVG data for weather condition"""
        # Clear/Sunny
        if weather_id == 800:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <circle cx="32" cy="32" r="12" fill="#FFD700"/>
                <line x1="32" y1="8" x2="32" y2="16" stroke="#FFD700" stroke-width="3"/>
                <line x1="32" y1="48" x2="32" y2="56" stroke="#FFD700" stroke-width="3"/>
                <line x1="8" y1="32" x2="16" y2="32" stroke="#FFD700" stroke-width="3"/>
                <line x1="48" y1="32" x2="56" y2="32" stroke="#FFD700" stroke-width="3"/>
                <line x1="14" y1="14" x2="20" y2="20" stroke="#FFD700" stroke-width="3"/>
                <line x1="44" y1="44" x2="50" y2="50" stroke="#FFD700" stroke-width="3"/>
                <line x1="50" y1="14" x2="44" y2="20" stroke="#FFD700" stroke-width="3"/>
                <line x1="20" y1="44" x2="14" y2="50" stroke="#FFD700" stroke-width="3"/>
            </svg>"""
        # Cloudy
        elif weather_id > 802:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="28" cy="36" rx="16" ry="12" fill="#95A5A6"/>
                <ellipse cx="40" cy="32" rx="14" ry="10" fill="#BDC3C7"/>
                <ellipse cx="20" cy="32" rx="12" ry="9" fill="#7F8C8D"/>
            </svg>"""
        # Partly Cloudy
        elif weather_id == 801 or weather_id == 802:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <circle cx="24" cy="20" r="10" fill="#FFD700"/>
                <line x1="24" y1="6" x2="24" y2="12" stroke="#FFD700" stroke-width="2"/>
                <line x1="10" y1="20" x2="16" y2="20" stroke="#FFD700" stroke-width="2"/>
                <ellipse cx="35" cy="40" rx="16" ry="11" fill="#BDC3C7"/>
                <ellipse cx="22" cy="38" rx="12" ry="9" fill="#95A5A6"/>
            </svg>"""
        # Rain
        elif 500 <= weather_id < 600:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="32" cy="24" rx="18" ry="12" fill="#95A5A6"/>
                <line x1="22" y1="38" x2="20" y2="48" stroke="#3498DB" stroke-width="3"/>
                <line x1="32" y1="38" x2="30" y2="48" stroke="#3498DB" stroke-width="3"/>
                <line x1="42" y1="38" x2="40" y2="48" stroke="#3498DB" stroke-width="3"/>
            </svg>"""
        # Snow
        elif 600 <= weather_id < 700:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="32" cy="24" rx="18" ry="12" fill="#95A5A6"/>
                <circle cx="22" cy="42" r="3" fill="#ECF0F1"/>
                <circle cx="32" cy="44" r="3" fill="#ECF0F1"/>
                <circle cx="42" cy="42" r="3" fill="#ECF0F1"/>
                <circle cx="27" cy="50" r="3" fill="#ECF0F1"/>
                <circle cx="37" cy="50" r="3" fill="#ECF0F1"/>
            </svg>"""
        # Thunderstorm
        elif 200 <= weather_id < 300:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="32" cy="20" rx="18" ry="12" fill="#7F8C8D"/>
                <polygon points="32,28 28,40 34,40 30,52 38,36 32,36" fill="#FFD700"/>
            </svg>"""
        # Drizzle/Mist
        else:
            return """<svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="32" cy="24" rx="18" ry="12" fill="#BDC3C7"/>
                <line x1="20" y1="38" x2="20" y2="44" stroke="#5DADE2" stroke-width="2"/>
                <line x1="28" y1="40" x2="28" y2="46" stroke="#5DADE2" stroke-width="2"/>
                <line x1="36" y1="38" x2="36" y2="44" stroke="#5DADE2" stroke-width="2"/>
                <line x1="44" y1="40" x2="44" y2="46" stroke="#5DADE2" stroke-width="2"/>
            </svg>"""

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
                    svg_data = self.get_weather_svg(weather_id)
                    day_widget.icon_widget.load(QByteArray(svg_data.encode()))

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