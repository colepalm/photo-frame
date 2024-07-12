from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget

from config import api_key, city_name
from ui.time_module import TimeWidget
from ui.weather_module import WeatherWidget
from utils import fetch_weather, load_photos


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")
        self.showFullScreen()

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")

        # Image label setup
        self.image_label = QLabel(central_widget)
        self.image_label.setGeometry(0, 0, self.width(), self.height())
        self.image_label.setScaledContents(True)

        self.weather_widget = WeatherWidget(self, api_key, city_name)
        self.weather_widget.setGeometry(self.width() - 300, 20, 280, 50)

        self.time_widget = TimeWidget(self)
        self.time_widget.setGeometry(650, self.height() - 100, 200, 100)

        self.photos_dir = './photos'
        self.photos_list = self.load_photos()
        self.current_photo = 0

        self.timer = QTimer(self)
        self.start_image_loop()

        self.update_image()
        self.update_positions()  # Update positions based on the full screen size

    def resizeEvent(self, event):
        """Handle the resize event to update widget positions."""
        if hasattr(self, 'image_label') and hasattr(self, 'weather_label') and hasattr(self, 'time_label'):
            self.update_positions()
        super().resizeEvent(event)

    def update_positions(self):
        """ Update positions of labels based on the current size of the window """
        screen_size = self.size()
        screen_size = self.size()
        self.image_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
        self.weather_widget.setGeometry(screen_size.width() - self.weather_widget.width() - 20, 20, 280, 50)
        self.time_widget.setGeometry(screen_size.width() - 300 - 20, screen_size.height() - 50 - 20, 300, 50)

    def load_photos(self):
        """Load the paths of photos in the directory."""
        return load_photos(self.photos_dir)

    def update_image(self):
        """Update the image displayed on the label."""
        if not self.photos_list:
            print("No images found in the directory.")
            return

        photo_path = self.photos_list[self.current_photo]
        pixmap = QPixmap(photo_path)
        self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.current_photo = (self.current_photo + 1) % len(self.photos_list)

    def start_image_loop(self):
        """Change the photo at intervals."""
        self.timer.timeout.connect(self.update_image)
        self.timer.start(120000)  # Change image every 120 seconds
