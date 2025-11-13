import io
import random

from PIL import Image
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget

from config import api_key, city_name
from ui.calendar_module import CalendarWidget
from ui.forecast_view import ForecastView
from ui.moon_sun_widget import MoonSunWidget
from ui.time_module import TimeWidget
from ui.weather_module import WeatherWidget
from utils import load_photos


def load_and_process_image(image_path):
    """Load an image and apply EXIF orientation correction."""
    try:
        from PIL import ImageOps

        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')

            img = ImageOps.exif_transpose(img)

            # Convert to QPixmap
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)

            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())

            return pixmap

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return QPixmap(image_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pixmap = None
        self.setWindowTitle("Digital Photo Frame")

        self.initial_setup_done = False  # Flag to ensure setup is done before handling resize events

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")

        self.image_label = QLabel(central_widget)
        self.image_label.setGeometry(0, 0, self.width(), self.height())
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.weather_widget = WeatherWidget(central_widget, api_key, city_name)
        self.weather_widget.setGeometry(self.width() - 300, 20, 280, 60)

        self.time_widget = TimeWidget(central_widget)
        self.time_widget.setGeometry(650, self.height() - 100, 200, 100)

        self.calendar_widget = CalendarWidget(central_widget)

        self.moon_sun_widget = MoonSunWidget(
            city="Denver",
            region="USA",
            timezone="America/Denver",
            lat=39.7872326,
            lon=-104.9973032,
            parent=central_widget
        )

        self.forecast_view = ForecastView(central_widget, api_key, city_name)
        self.forecast_view.hide()  # Initially hidden

        self.showing_forecast = False

        # Timer to show forecast view periodically
        self.forecast_display_timer = QTimer(self)
        self.forecast_display_timer.timeout.connect(self.show_forecast_temporarily)
        self.forecast_display_timer.start(600000)  # Show every 10 minutes

        # Timer to hide forecast view after displaying
        self.forecast_hide_timer = QTimer(self)
        self.forecast_hide_timer.timeout.connect(self.hide_forecast_view)
        self.forecast_hide_timer.setSingleShot(True)

        self.photos_list = load_photos()
        random.shuffle(self.photos_list)
        self.current_photo = 0

        self.timer = QTimer(self)
        self.start_image_loop()

        self.update_image()
        self.update_positions()  # Update positions based on the full screen size

        self.initial_setup_done = True  # Mark the setup as complete
        self.showFullScreen()

    def resizeEvent(self, event):
        """Handle the resize event to update widget positions."""
        if self.initial_setup_done:
            print("Resizing window")
            self.update_positions()
            # Update the current image to fit the new size
            self.update_current_image_size()
        super().resizeEvent(event)

    def update_current_image_size(self):
        """Update the current image to fit the new window size."""
        if hasattr(self, 'current_pixmap') and self.current_pixmap:
            scaled_pixmap = self.current_pixmap.scaled(
                self.image_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def update_positions(self):
        """ Update positions of labels based on the current size of the window """
        screen_size = self.size()
        self.image_label.setGeometry(0, 0, screen_size.width(), screen_size.height())

        weather_widget_width = min(280, screen_size.width() // 4)
        weather_margin = 20
        weather_widget_height = min(100, screen_size.height() // 15)

        weather_x = max(weather_margin, screen_size.width() - weather_widget_width - weather_margin)
        weather_y = weather_margin
        weather_y = max(weather_margin, min(weather_y, screen_size.height() - weather_widget_height - weather_margin))

        self.weather_widget.setGeometry(
            weather_x,
            weather_y,
            weather_widget_width,
            weather_widget_height
        )

        time_widget_height = 60
        time_widget_width = 200
        self.time_widget.setGeometry(
            screen_size.width() - time_widget_width - 20,
            screen_size.height() - time_widget_height - 20,
            time_widget_width,
            time_widget_height
        )

        calendar_widget_width = 200
        self.calendar_widget.setFixedWidth(calendar_widget_width)
        self.calendar_widget.adjustSize()
        self.calendar_widget.move(
            20,
            screen_size.height() - self.calendar_widget.height() - 20
        )

        moon_sun_width = 200
        moon_sun_height = 60
        self.moon_sun_widget.setGeometry(
            20,
            20,
            moon_sun_width,
            moon_sun_height
        )

        # Update forecast view position if it's showing
        if self.showing_forecast:
            self.update_forecast_view_position()

    def update_image(self):
        """Update the image displayed on the label."""
        if not self.photos_list:
            print("No images found in the directory.")
            return

        photo_path = self.photos_list[self.current_photo]
        print(f"Loading image: {photo_path}")

        # Load and process the image with EXIF orientation correction
        pixmap = load_and_process_image(photo_path)

        # Store the original pixmap for resizing
        self.current_pixmap = pixmap

        # Scale the image to fit the label
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.current_photo = (self.current_photo + 1) % len(self.photos_list)

    def start_image_loop(self):
        """Change the photo at intervals."""
        self.timer.timeout.connect(self.update_image)
        self.timer.start(120000)  # Change image every 120 seconds

    def show_forecast_temporarily(self):
        """Show the forecast view temporarily"""
        if not self.showing_forecast:
            self.update_forecast_view_position()
            self.forecast_view.show()
            self.forecast_view.raise_()  # Bring to front
            self.showing_forecast = True
            # Hide after 30 seconds
            self.forecast_hide_timer.start(30000)

    def hide_forecast_view(self):
        """Hide the forecast view"""
        self.forecast_view.hide()
        self.showing_forecast = False

    def update_forecast_view_position(self):
        """Position the forecast view to cover most of the screen"""
        screen_size = self.size()

        # Make it take up most of the screen with margins
        margin = 50
        self.forecast_view.setGeometry(
            margin,
            margin,
            screen_size.width() - (margin * 2),
            screen_size.height() - (margin * 2)
        )