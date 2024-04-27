import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt


class PhotoFrameApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Photo Frame")
        self.showFullScreen()

        self.last_size = None  # Track the last size to prevent unnecessary updates

        # Central widget to hold the image
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: black;")

        # Image label
        self.image_label = QLabel()
        self.image_label.setScaledContents(True)

        # Top right corner for weather information
        self.weather_label = QLabel("Loading weather...")
        self.weather_label.setFont(QFont('Arial', 16))
        self.weather_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")

        self.timer = QTimer()

        # TODO: Requery weather periodically
        # self.weatherUpdateTimer = QTimer(self)
        # self.weatherUpdateTimer.timeout.connect(self.update_weather)
        # self.weatherUpdateTimer.start(600000)  # 10 minutes in milliseconds

        # Horizontal layout for the bottom right time display
        self.time_label = QLabel("00:00", self)
        self.time_label.setFont(QFont('Arial', 18))
        self.time_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 100);")

        self.photos_dir = './photos'
        self.photos_list = self.load_photos()
        self.current_photo = 0

        self.update_image()
        self.start_image_loop()
        self.update_positions()  # Update positions based on the full screen size

    def resizeEvent(self, event):
        # Call to update positions if the size actually changes
        if hasattr(self, 'last_size'):
            if not self.last_size or event.size() != self.last_size:
                self.update_positions()  # Update positions on resize event
                self.last_size = event.size()
        super().resizeEvent(event)

    def update_positions(self):
        """ Update positions of labels based on the current size of the window """
        if hasattr(self, 'image_label') and hasattr(self, 'weather_label') and hasattr(self, 'time_label'):
            screen_size = self.size()
            self.image_label.setGeometry(0, 0, screen_size.width(), screen_size.height())
            self.weather_label.move(screen_size.width() - self.weather_label.width() - 20, 20)
            self.time_label.move(screen_size.width() - self.time_label.width() - 20,
                                 screen_size.height() - self.time_label.height() - 20)

    def load_photos(self):
        """Load the paths of photos in the directory."""
        files = [os.path.join(self.photos_dir, f) for f in os.listdir(self.photos_dir) if
                 f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return files

    def update_image(self):
        """Update the image displayed on the label."""
        if not self.photos_list:
            print("No images found in the directory.")
            return

        photo_path = self.photos_list[self.current_photo]
        pixmap = QPixmap(photo_path)

        # Scale the pixmap to fit the label while maintaining the aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.image_label.setPixmap(scaled_pixmap)

        # Cycle through the photo list
        self.current_photo += 1
        if self.current_photo >= len(self.photos_list):
            self.current_photo = 0

    def start_image_loop(self):
        """Change the photo at intervals."""
        self.timer.timeout.connect(self.update_image)
        self.timer.start(120000)  # Change image every 120 seconds

    def update_time(self):
        # Update time label
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def update_weather(self):
        # Fetch and update weather
        # Use your existing logic
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoFrameApp()
    window.show()
    sys.exit(app.exec_())
