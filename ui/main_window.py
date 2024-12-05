from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget

from config import api_key, city_name
from ui.calendar_module import CalendarWidget
from ui.time_module import TimeWidget
from ui.weather_module import WeatherWidget
from utils import load_photos


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")

        self.initial_setup_done = False  # Flag to ensure setup is done before handling resize events

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")

        self.image_label = QLabel(central_widget)
        self.image_label.setGeometry(0, 0, self.width(), self.height())
        self.image_label.setScaledContents(True)

        self.weather_widget = WeatherWidget(central_widget, api_key, city_name)
        self.weather_widget.setGeometry(self.width() - 300, 20, 280, 50)

        self.time_widget = TimeWidget(central_widget)
        self.time_widget.setGeometry(650, self.height() - 100, 200, 100)

        self.calendar_widget = CalendarWidget(central_widget)

        self.photos_dir = './photos'
        self.photos_list = self.load_photos()
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
        super().resizeEvent(event)

    def update_positions(self):
        """ Update positions of labels based on the current size of the window """
        screen_size = self.size()
        self.image_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
        weather_widget_width = 200
        self.weather_widget.setGeometry(screen_size.width() - weather_widget_width - 20, 20,
                                        weather_widget_width, 50)
        time_widget_height = 60
        self.time_widget.setGeometry(screen_size.width() - 300 - 20, screen_size.height() - time_widget_height - 20,
                                     300, time_widget_height)

        calendar_widget_width = 200
        calendar_widget_height = 90
        self.calendar_widget.setGeometry(20, screen_size.height() - calendar_widget_height - 20, calendar_widget_width,
                                         calendar_widget_height)
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
